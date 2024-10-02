// Only for control dependence info in Version 1.0

#include "PMDependency.h"

#define DEBUG_TYPE "depa"
//#define LLVM_DEBUG(x) x


using namespace llvm;

namespace pminv {

  void PMDependency::PostOrderTraversePDT(DomTreeNode *node) {

    assert(PDTreeRootNode != nullptr || F.getBasicBlockList().size() == 1);

        if (node->getChildren().empty()) {
            auto *bb = node->getBlock();
            for (auto *pred : predecessors(bb)) {
                auto *predNode = PDT.getNode(pred);
                if (predNode->getIDom() != node) {
                    PostDomFrontierMap[bb].push_back(predNode->getBlock());
                }
            }
            LLVM_DEBUG(dbgs() << "Visit : " << node->getBlock()->front() << "\n");
            return;
        }

        for(auto *domTreeNode : node->getChildren()) {
            PostOrderTraversePDT(domTreeNode);
        }

        auto *bb = node->getBlock();
        for (auto *pred : predecessors(bb)) {
            auto *predNode = PDT.getNode(pred);
            if(predNode->getIDom() != node) {
                PostDomFrontierMap[bb].push_back(predNode->getBlock());
            }
        }
        for (auto *child : node->getChildren()) {
            auto *childBB = child->getBlock();
            for (auto *childFrontierBB : PostDomFrontierMap[childBB]) {
                auto *childFrontierNode = PDT.getNode(childFrontierBB);
                if (childFrontierNode && childFrontierNode->getIDom() && childFrontierNode->getIDom() != node) {
                    PostDomFrontierMap[bb].push_back(childFrontierNode->getBlock());
                }
            }
        }
        LLVM_DEBUG(dbgs() << "Visit : " << node->getBlock()->front() << "\n");

    }


    void PMDependency::SetPDTRootNode() {

      LLVM_DEBUG(dbgs() << PDT.isPostDominator() << "\n ");
        LLVM_DEBUG(dbgs() << F.getName() << "\n");
        for (BasicBlock &bb : F) {
            DomTreeNode *node;
            if(PDT.getNode(&bb))
                node = PDT.getNode(&bb);
            else
                continue;
            assert(node!= nullptr);
            LLVM_DEBUG(dbgs()  << bb.front() << " Level : " << node->getLevel() << "\n");
            if (node->getLevel() == 1) PDTreeRootNode = node;

            SmallVector<BasicBlock*, 8> Result;
            PDT.getDescendants(&bb, Result);
            if (Result.empty()) {
                LLVM_DEBUG(dbgs() << "No BB dominates : " << bb.front() << "\n");
            }
            else {
                for (BasicBlock *bb : Result)
                    LLVM_DEBUG(dbgs() << "dominates : " << bb->front() << "\n");
            }
        }
    }

    void PMDependency::ControlDepBuilder() {

      assert(!PostDomFrontierMap.empty() || F.getBasicBlockList().size() == 1);

      for (auto item : PostDomFrontierMap) {
            BasicBlock* bb = item.first;
            LLVM_DEBUG(dbgs()  << bb << "\n");
            SmallVector<BasicBlock*, 8> PDFrontier = item.second;
            for(BasicBlock* frontier : PDFrontier) {
                LLVM_DEBUG(dbgs()  << "Adding Froniter " << *frontier << " to " << *bb);
                ControlDepMap[frontier].push_back(bb);
            }
        }

    }

    void PMDependency::CDGWriter() {

      assert(!ControlDepMap.empty() || F.getBasicBlockList().size() == 1);

      LLVM_DEBUG(dbgs() << F.getParent()->getModuleIdentifier() << "\n");
        std::string filename = F.getParent()->getModuleIdentifier();
        if(filename.find('/')) {
            filename = filename.substr(filename.find_last_of('/')+1);
            filename = filename.substr(0, filename.size()-3);
        }
        LLVM_DEBUG(dbgs() << filename << "\n");
        std::string dotName =  "dot/"+ filename + "." + F.getName().str() + ".cd.dot";
        std::error_code EC;
        raw_fd_ostream out(dotName, EC);

        assert(!EC.message().empty());
        out << "digraph \"CDG for '" << F.getName().str() << "' function\" {\n";
        out << "\tlabel=\"CDG for '" << F.getName().str() << "' function\";\n\n";
        std::set<BasicBlock*> CDGnodes;
        for (auto item : ControlDepMap) {
            BasicBlock* bb = item.first;
            LLVM_DEBUG(dbgs()  << bb << "\n");
            CDGnodes.insert(bb);
            out << "\tNode" << bb << " [shape=record,label=\"{" << bb->getName();
            for(Instruction& i : *bb) {
                out << i << "\\l";
            }
            out << "}\"];\n";
        }

        for (auto item : ControlDepMap) {
            BasicBlock* bb = item.first;
            SmallVector<BasicBlock*, 8> CDbbs = item.second;
            for(BasicBlock* CDbb : CDbbs) {
                if(!CDGnodes.count((CDbb))) {
                    CDGnodes.insert(CDbb);
                    out << "\tNode" << CDbb << " [shape=record,label=\"{" << CDbb->getName();
                    for(Instruction& i : *CDbb) {
                        out << i << "\\l";
                    }
                    out << "}\"];\n";
                }
                out << "\tNode" << bb << " -> Node" << CDbb <<";\n";
            }
        }
        out <<"}";
        out.close();
    }

    void PMDependency::ControlDepAnalysis(){
        LLVM_DEBUG(dbgs() << "----------BEGIN CONTROL DEPENDENCE ANALYSIS-----------\n");
        SetPDTRootNode();
        PostOrderTraversePDT(PDTreeRootNode);
        ControlDepBuilder();
        MemoryDepAnalysis();
        LLVM_DEBUG(dbgs() << "----------END MEMORY CONTROL DEPENDENCE ANALYSIS-----------\n");
    }

    void PMDependency::MemoryDepAnalysis() {
        //         Compute Control PMDependency:
        //         Reverse Post Dominator Frontiers Graph to get Control Dependence Graph
        //         Post order traversal of Post Dom Tree to get PostDomFrontier Graph
        //          for each X in a post-order traversal of the post-dominator tree do:
        //          PostDominanceFrontier(X) ← ∅
        //          for each Y ∈ Predecessors(X) do:
        //            if immediatePostDominator(Y) ≠ X:
        //              then PostDominanceFrontier(X) ← PostDominanceFrontier(X) ∪ {Y}
        //          done
        //          for each Z ∈ Children(X) do:
        //            for each Y ∈ PostDominanceFrontier(Z) do:
        //              if immediatePostDominator(Y) ≠ X:
        //                then PostDominanceFrontier(X) ← PostDominanceFrontier(X) ∪ {Y}
        //            done
        //          done
        //        done
        assert(!ControlDepMap.empty() || F.getBasicBlockList().size() == 1);

        for (const auto& item : ControlDepMap) {
            BasicBlock* bb = item.first;
            SmallVector<BasicBlock*, 8> CDbbs = item.second;
	    //            Instruction* CDI;

            LLVM_DEBUG(dbgs()  << __func__ << " : " << bb  << "\n");

            SmallVector<Instruction*, 8> CDIs;
            // We check all loads since not all of them from the struct variables defined
            for (Instruction &i : *bb) {
                if(isa<LoadInst>(i)) {
                    CDIs.push_back(&i);
                    LLVM_DEBUG(dbgs() << "LOAD POINT: " << i << "\n");
                }
            }
            for (BasicBlock *CDbb : CDbbs) {
                for(Instruction &CDBBi : *CDbb) {
                    if(isa<StoreInst>(CDBBi) || isa<LoadInst>(CDBBi)) {
//                    if(isa<LoadInst>(CDBBi)) {
                        for (auto CDI : CDIs)
                            MemoryDepMap[&CDBBi].push_back(CDI);
                    }
                }
            }
        }

    }

    void PMDependency::GEPAnalysis() {
        for (BasicBlock &BB : F) {
            for (auto &I : BB) {
                if (GetElementPtrInst* GEPI = dyn_cast<GetElementPtrInst>(&I)) {
                    Value* val = GEPI->getPointerOperand();
                    if (Instruction* depI = dyn_cast<Instruction>(val)) {
                        MemoryDepMap[&I].push_back(depI);
                    }
                    LLVM_DEBUG(dbgs() << *val << "\n");
                    if (val->getType()->isStructTy()) {
                        LLVM_DEBUG(dbgs() << *val << "\n");
                    }
                }
            }
        }
    }

    void PMDependency::DataDepAnalysis() {
        LLVM_DEBUG(dbgs() << "----------BEGIN MEMORY SSA DEPENDENCE ANALYSIS-----------\n");

        // Should use Memory SSA to restrict order too!
        for (BasicBlock &bb : F) {
            MemoryPhi *mphi = MSSA.getMemoryAccess(&bb);
            for (Instruction &i : bb) {
                if (MSSA.getMemoryAccess(&i)) {
                    MemoryUseOrDef *ma = MSSA.getMemoryAccess(&i);
                    LLVM_DEBUG(dbgs()  << i << " : " << *ma << "\n");
                    if (dyn_cast<MemoryUse>(ma)) {
                        MemoryUse *mu = dyn_cast<MemoryUse>(ma);
                        if (!DataDepMap.count(mu->getMemoryInst())) {
                            DataDepMap[mu->getMemoryInst()] = SmallVector<Instruction*, 8>{};
                        }
                        LLVM_DEBUG(dbgs() << "Memory Use : " << *mu << " : " << *mu->getOperand(0) << " : \n");
                        MemoryAccess *muo = mu->getOperand(0);
                        if (dyn_cast<MemoryUse>(muo)) {
                            MemoryUse *muu = dyn_cast<MemoryUse>(muo);
                            if (muu->getMemoryInst()) {
                                LLVM_DEBUG(dbgs()  << " Depends on : " << *muu << " inst : " <<  *muu->getMemoryInst() << "\n");
                                DataDepMap[mu->getMemoryInst()].push_back(muu->getMemoryInst());
                            }
                        }
                        else if (dyn_cast<MemoryDef>(muo)) {
                            MemoryDef *mud = dyn_cast<MemoryDef>(muo);
                            if (mud->getMemoryInst()) {
                                LLVM_DEBUG(dbgs()  << " Depends on : " << *mud << " inst : " << *mud->getMemoryInst() << "\n");
                                DataDepMap[mu->getMemoryInst()].push_back(mud->getMemoryInst());
                            }
                        }
                        else if (dyn_cast<MemoryPhi>(muo)){
                            MemoryPhi *muphi = dyn_cast<MemoryPhi>(muo);
                            for (int i = 0; i < muphi->getNumOperands(); ++i) {
                                MemoryAccess *memoryUseOrDef = muphi->getOperand(i);
                                if(dyn_cast<MemoryDef>(memoryUseOrDef)) {
                                    MemoryDef *muphiDef = dyn_cast<MemoryDef>(memoryUseOrDef);
                                    if (muphiDef->getMemoryInst()) {
                                        LLVM_DEBUG(dbgs()  << " Depends on : " << *muphiDef << " inst : " << *muphiDef->getMemoryInst() << "\n");
                                        DataDepMap[mu->getMemoryInst()].push_back(muphiDef->getMemoryInst());
                                    }
                                }
                                else if (dyn_cast<MemoryUse>(memoryUseOrDef)) {
                                    MemoryUse *muphiUse = dyn_cast<MemoryUse>(memoryUseOrDef);
                                    if (muphiUse->getMemoryInst()) {
                                        LLVM_DEBUG(dbgs()  << " Depends on : " << *muphiUse << " inst : " << *muphiUse->getMemoryInst() << "\n");
                                        DataDepMap[mu->getMemoryInst()].push_back(muphiUse->getMemoryInst());

                                    }
                                }
                            }
                        }
                    }
                    else if (dyn_cast<MemoryDef>(ma)) {
                        MemoryDef *md = dyn_cast<MemoryDef>(ma);
                        LLVM_DEBUG(dbgs() << "Memory Def : " << *md << " : " << *md->getOperand(0) << " : ");
                        MemoryAccess *mdo = md->getOperand(0);
                        if (dyn_cast<MemoryUse>(mdo)) {
                            MemoryUse *mdu = dyn_cast<MemoryUse>(mdo);
                            if (mdu->getMemoryInst()){
                                LLVM_DEBUG(dbgs()  << " Depends on : " << *mdu << " inst : " << *mdu->getMemoryInst() << "\n");
                                DataDepMap[md->getMemoryInst()].push_back(mdu->getMemoryInst());
                            }
                        }
                        else if (dyn_cast<MemoryDef>(mdo)) {
                            MemoryDef *mdd = dyn_cast<MemoryDef>(mdo);
                            if (mdd->getMemoryInst()){
                                LLVM_DEBUG(dbgs()  << " Depends on : " << *mdd << " inst : " << *mdd->getMemoryInst() << "\n");
                                DataDepMap[md->getMemoryInst()].push_back(mdd->getMemoryInst());
                            }
                        }
                        else if (dyn_cast<MemoryPhi>(mdo)){
                            MemoryPhi *muphi = dyn_cast<MemoryPhi>(mdo);
                            for (int i = 0; i < muphi->getNumOperands(); ++i) {
                                MemoryAccess *memoryUseOrDef = muphi->getOperand(i);
                                if(dyn_cast<MemoryDef>(memoryUseOrDef)) {
                                    MemoryDef *muphiDef = dyn_cast<MemoryDef>(memoryUseOrDef);
                                    if (muphiDef->getMemoryInst()) {
                                        DataDepMap[md->getMemoryInst()].push_back(muphiDef->getMemoryInst());
                                        LLVM_DEBUG(dbgs()  << " Depends on : " << *muphiDef << " inst : " << *muphiDef->getMemoryInst() << "\n");
                                    }
                                }
                                else if (dyn_cast<MemoryUse>(memoryUseOrDef)) {
                                    MemoryUse *muphiUse = dyn_cast<MemoryUse>(memoryUseOrDef);
                                    if (muphiUse->getMemoryInst()) {
                                        DataDepMap[md->getMemoryInst()].push_back(muphiUse->getMemoryInst());
                                        LLVM_DEBUG(dbgs()  << " Depends on : " << *muphiUse << " inst : " << *muphiUse->getMemoryInst() << "\n");
                                    }
                                }
                            }
                        }
                    }
                    else {
                        assert(false && "Wrong Memorry SSA cast !");
                    }
                    LLVM_DEBUG(dbgs()<< "\n");
                }
            }
        }
        LLVM_DEBUG(dbgs() << "----------END MEMORY SSA DEPENDENCE ANALYSIS-----------\n");

    }
}
