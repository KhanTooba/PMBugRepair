#ifndef PM_INVARIANT_GENERATION_PMDEPENDENCY_H
#define PM_INVARIANT_GENERATION_PMDEPENDENCY_H

#include "llvm/Analysis/DependenceAnalysis.h"
#include "llvm/Analysis/DominanceFrontier.h"
#include "llvm/Analysis/PostDominators.h"
#include "llvm/Analysis/CFG.h"
#include "llvm/Analysis/MemorySSA.h"
#include "llvm/Analysis/MemoryDependenceAnalysis.h"

#include "llvm/IR/Function.h"
#include "llvm/IR/InstVisitor.h"
#include "llvm/IR/Constant.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Instruction.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Dominators.h"
#include "llvm/IR/DerivedTypes.h"
#include "llvm/IR/DebugInfoMetadata.h"

#include "llvm/Pass.h"
#include "llvm/Support/ErrorHandling.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/ADT/SmallVector.h"
#include "llvm/ADT/MapVector.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

namespace pminv {

class PMDependency {
private:
    Function &F;
    PostDominatorTree &PDT;
    DependenceInfo &DI;
    MemorySSA &MSSA;

    MapVector<BasicBlock*, SmallVector<BasicBlock*, 8>> ControlDepMap;
    MapVector<Instruction*, SmallVector<Instruction*, 8>> DataDepMap;
    MapVector<Instruction*, SmallVector<Instruction*, 8>> MemoryDepMap;
    MapVector<BasicBlock*, SmallVector<BasicBlock*, 8>> PostDomFrontierMap;

    DomTreeNode *PDTreeRootNode;

public:
    PMDependency(Function &f, PostDominatorTree &pdt, DependenceInfo &di, MemorySSA &mssa)
                : F(f), PDT(pdt), DI(di), MSSA(mssa) {};

    void PostOrderTraversePDT(DomTreeNode *node);
    void SetPDTRootNode();
    void CDGWriter();
    void ControlDepBuilder();
    void ControlDepAnalysis();
    void MemoryDepAnalysis();
    void DataDepAnalysis();
    auto GetMemoryControlDepMap() { return MemoryDepMap; };

    auto GetDataDepMap() { return DataDepMap; };


    void GEPAnalysis();
};

};
#endif //PM_INVARIANT_GENERATION_PMDEPENDENCY_H
