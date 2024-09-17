#include "llvm/Analysis/DependenceAnalysis.h"
#include "llvm/Analysis/DominanceFrontier.h"
#include "llvm/Analysis/PostDominators.h"
#include "llvm/Analysis/MemorySSA.h"
#include "llvm/Analysis/MemoryDependenceAnalysis.h"
#include "llvm/Analysis/BasicAliasAnalysis.h"
#include "llvm/Analysis/GlobalsModRef.h"
#include "llvm/Analysis/AliasSetTracker.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/InstVisitor.h"
#include "llvm/IR/Constant.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Instruction.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Dominators.h"
#include "llvm/IR/Use.h"
#include "llvm/IR/User.h"
#include "llvm/IR/Value.h"
#include "llvm/IR/DerivedTypes.h"
#include "llvm/Pass.h"
#include "llvm/PassAnalysisSupport.h"
#include "llvm/Support/ErrorHandling.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/DerivedTypes.h"
#include "llvm/IR/DebugInfoMetadata.h"
#include "llvm/IR/DebugInfo.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Module.h"

//Added by Tooba
#include "llvm/IR/InlineAsm.h"
#include <string>
#include "llvm/Support/raw_ostream.h"
//Addition by Tooba ends

#include <iostream>
#include <fstream>
#include <deque>

#include "PMDependency.h"

using namespace llvm;

#define DEBUG_TYPE "pmtrace"
//#define LLVM_DEBUGx(x) x

namespace pminv {

  struct PMTraceGen : public FunctionPass, public InstVisitor<PMTraceGen> {

    static char ID;

    PMTraceGen() : FunctionPass(ID) {}

    // add the "UniqueID" metadata to each instruction (for debugging)
    unsigned long uniqueID = 0;
    
    FunctionCallee  __pmc_Initialize,  __pmc_depAdd, __pmc_printStoreAddr, __pmc_printLoadAddr,  __pmc_funcBegin, __pmc_funcEnd;

    MapVector<Instruction *, SmallVector<Instruction *, 8>> MemoryControlDepMap;
    MapVector<Instruction *, SmallVector<Instruction *, 8>> DataDepMap;

    std::set<int> PrintedIDs;

    // Instruction Debug Info
    MapVector<Instruction *, int> InstToIDMap;
    std::map<Instruction *, std::string> InstToSubProgramName;
    // Only for load and store instructions
    std::map<unsigned, std::string> InstIDToNameMap;

    MapVector<Instruction *, unsigned> InstToIncMap;
    std::map<std::string, std::vector<Type *>> StructFields;
    MapVector<StructType *, unsigned> StTypeToSize;

    //GlobalVariable *GV_Inst_Counter;

    // std::set<Function*> annotFuncs;

        llvm::Type *i32_type, *i64_type;
        Module *M;
        // Get the unique ID metadata kind

        bool Init = false;
        // Initialize external functions from helper function

    void init( Function &F ) {
        // llvm::outs() << "Initializing pass...\n";

        if (Init)
          return; 

        Init = true;

        i32_type = llvm::IntegerType::getInt32Ty(F.getContext());
        i64_type = llvm::IntegerType::getInt64Ty(F.getContext());

        LLVMContext &ctx = F.getContext();
        M = F.getParent();

        __pmc_Initialize = M->getOrInsertFunction("__pmc_Initialize", Type::getVoidTy(ctx)  );
        //LLVM_DEBUG(dbgs() << "found __pmc_Initialize function " << __pmc_Initialize.getFunctionType() << "\n");
        __pmc_depAdd = M->getOrInsertFunction("__pmc_depAdd", Type::getVoidTy(ctx), 
                Type::getInt32Ty(ctx),
                Type::getInt32Ty(ctx)  );
        //LLVM_DEBUG(dbgs() << "found __pmc_depAdd function " << __pmc_depAdd.getFunctionType() << "\n");
        __pmc_printStoreAddr = M->getOrInsertFunction("__pmc_printStoreAddr", Type::getVoidTy(ctx), 
                  Type::getInt64Ty(ctx),
                  Type::getInt32Ty(ctx),
                  Type::getInt32Ty(ctx),
                  Type::getInt32Ty(ctx),
                  Type::getInt32Ty(ctx),
                    Type::getInt8PtrTy(ctx) );
        //LLVM_DEBUG(dbgs() << "found __pmc_printStoreAddr function " << *__pmc_printStoreAddr.getFunctionType() << "\n");
        __pmc_printLoadAddr = M->getOrInsertFunction("__pmc_printLoadAddr", Type::getVoidTy(ctx), 
                      Type::getInt64Ty(ctx),
                      Type::getInt32Ty(ctx),
                      Type::getInt32Ty(ctx),
                      Type::getInt32Ty(ctx),
                      Type::getInt32Ty(ctx),
                      Type::getInt8PtrTy(ctx) );	   
        //LLVM_DEBUG(dbgs() << "found __pmc_printLoadAddr function " << *__pmc_printLoadAddr.getFunctionType() << "\n");
        __pmc_funcBegin = M->getOrInsertFunction("__pmc_funcBegin", Type::getVoidTy(ctx), 
                  Type::getInt8PtrTy(ctx) );
        //LLVM_DEBUG(dbgs() << "found __pmc_funcBegin function " << __pmc_funcBegin.getFunctionType() << "\n");
        __pmc_funcEnd = M->getOrInsertFunction("__pmc_funcEnd", Type::getVoidTy(ctx), 
                Type::getInt8PtrTy(ctx) );
        //LLVM_DEBUG(dbgs() << "found __pmc_funcEnd function " << __pmc_funcEnd.getFunctionType() << "\n");
        /*
        __pmc_memAdd = M->getOrInsertFunction("__pmc_memAdd", Type::getVoidTy(ctx), 
                    Type::getInt64Ty(ctx),
                    Type::getInt64Ty(ctx) );
        //LLVM_DEBUG(dbgs() << "found __pmc_memAdd function " << __pmc_memAdd.getFunctionType() << "\n");
        __pmc_memRemove = M->getOrInsertFunction("__pmc_memRemove", Type::getVoidTy(ctx), 
                      Type::getInt64Ty(ctx) );
        //LLVM_DEBUG(dbgs() << "found __pmc_memRemove function " << __pmc_memRemove.getFunctionType() << "\n");
        __pmc_memClear = M->getOrInsertFunction("__pmc_memClear", Type::getVoidTy(ctx));
        //LLVM_DEBUG(dbgs() << "found __pmc_memClear function " << __pmc_memClear.getFunctionType() << "\n");
        __pmc_printDep = M->getOrInsertFunction("__pmc_printDep", Type::getVoidTy(ctx), 
                  Type::getInt32Ty(ctx), Type::getInt32Ty(ctx));
        //LLVM_DEBUG(dbgs() << "found __pmc_printDep function " << __pmc_printDep.getFunctionType() << "\n");
        */
      }

    virtual bool runOnFunction(Function &F) override {
      init(F);
	    insertFlush(F);
      insertFence(F);
        
      if (!F.getSubprogram()) {
        LLVM_DEBUG( dbgs() << __func__ << " (0) skip the Function " << F.getName() << " since it doesn't have debug information.\n");
        return false;
      }
      if (F.getSubprogram()->getFilename().contains("c++")) {
        LLVM_DEBUG( dbgs() << __func__ << " (1) skip the Function " << F.getName() << " FileName:  " << F.getSubprogram()->getFilename() << " Name: " << F.getSubprogram()->getName() << "\n");
        return false;
      }
      if (F.getName().contains("_GLOBAL__sub_I")  || F.getName().contains("__cxx_global_var_init") ){
        LLVM_DEBUG( dbgs() << __func__ << " (2) skip the Function " << F.getName() << " since it initializes <iostream>.\n");
        return false;
      }

      // Chao: the following lines are taken from 'PMSetUniqueID' pass
      
      SetInstUniqueID(F);
      InsertDummyBeginEnd(F);
      LLVM_DEBUG(dbgs() << "Function: " << F.getName() << " BlockSize: " << F.getBasicBlockList().size() << "\n");

      // Chao: the remaining lines are taken from 'PMTraceGen' pass
      
      GetUniqueID(F);
      
      LLVM_DEBUG( dbgs() <<F.getParent()->getSourceFileName()<< ": Instrumenting " << F.getName() << " BlockSize: " << F.getBasicBlockList().size() << "\n" );
      
      DependenceInfo &DI = getAnalysis<DependenceAnalysisWrapperPass>().getDI();
      PostDominatorTree &PDT = getAnalysis<PostDominatorTreeWrapperPass>().getPostDomTree();
      DominanceFrontier &DF = getAnalysis<DominanceFrontierWrapperPass>().getDominanceFrontier();
      BasicAAResult &BAAR = getAnalysis<BasicAAWrapperPass>().getResult();
      MemorySSA &MSSA = getAnalysis<MemorySSAWrapperPass>().getMSSA();

      PDT.recalculate(F);

      auto *dep = new PMDependency(F, PDT, DI, MSSA);
      dep->ControlDepAnalysis();
      dep->GEPAnalysis();
      dep->DataDepAnalysis();
      
      MemoryControlDepMap = dep->GetMemoryControlDepMap();
      DataDepMap = dep->GetDataDepMap();
      InstruDepMap(F);

      IRBuilder<> builder(F.getContext());
      //CreateGlob(builder, "Inst_Counter", F);
	    
      if (F.getName() == "main") {
        BasicBlock *entryBB = BasicBlock::Create(F.getParent()->getContext(), "entry", &F, &F.front());
        builder.SetInsertPoint(entryBB);
        builder.SetCurrentDebugLocation(DebugLoc());
        Value *creat_hs = builder.CreateCall(__pmc_Initialize);
        builder.CreateBr(F.begin()->getNextNode());
      }

      // recursively invoke "visitCallInst", "visitStoreInst", "visitLoadInst", etc.
      for (BasicBlock &bb: F) {
        for (Instruction &i: bb) {
          this->visit(i);
        }
      }

      for (BasicBlock &bb : F) {
        for (Instruction &i : bb) {
          InsertFuncBeginEnd(i);
        }
      }
      return true;
    }

    
    void InsertFuncBeginEnd(Instruction &i) {

	  if (i.getMetadata("__PMC_FunctionName")) {

	    IRBuilder<> builder(i.getContext());
                builder.SetInsertPoint(&i);
                if (auto *MD = i.getMetadata("__PMC_FunctionName")) {
                    if (auto *str = cast<MDString>(MD->getOperand(0))) {
                        StringRef mdstr = str->getString();
                        //LLVM_DEBUG( dbgs() << "PMC Metadata Value: " << mdstr << "\n");
                        //llvm::Constant *ScopeConstant = builder.CreateGlobalStringPtr(mdstr);
			llvm::Constant *ScopeConstant = getOrCreateGlobalStringPtr(&builder, mdstr);
                        llvm::ArrayRef< llvm::Value* > args = {ScopeConstant};
                        if (isa<CallInst>(i)) {
                            CallInst* CALLI = dyn_cast<CallInst>(&i);
                            if (CALLI->getCalledFunction()->getName() == "__pmc_dummy_begin") {
                                builder.CreateCall(__pmc_funcBegin, args);
                            }
                            else {
                                builder.CreateCall(__pmc_funcEnd, args);
                            }
                        }
                    }
                }
            }
        }

    /*
        GlobalVariable *CreateGlob(IRBuilder<> &Builder, std::string Name, Function &F) {
            F.getParent()->getOrInsertGlobal(Name, Builder.getInt32Ty());
            ConstantInt *const_int_val = ConstantInt::get(F.getParent()->getContext(), APInt(32, 0));
            GlobalVariable *gVar = F.getParent()->getNamedGlobal(Name);
            gVar->setInitializer(const_int_val);
            gVar->setLinkage(GlobalValue::CommonLinkage);
            gVar->setDSOLocal(true);
            return gVar;
        }
    */
    /*
        GlobalVariable *CreateGlobHash(IRBuilder<> &Builder, std::string Name, Function &F) {
	  F.getParent()->getOrInsertGlobal(Name, __pmc_Initialize.getFunctionType());
            Constant *NullValue = Constant::getNullValue(__pmc_Initialize.getFunctionType());
            GlobalVariable *gVar = F.getParent()->getNamedGlobal(Name);
            gVar->setInitializer(NullValue);
            gVar->setLinkage(GlobalValue::CommonLinkage);
            gVar->setDSOLocal(true);
            return gVar;
        }
    */
    // creating 'InstToIDMap' and 'instToSubProgramName' based on the 'UniqueID' metadata associated with each instruction 
    void GetUniqueID(Function &F) {

      for (BasicBlock &bb: F) {
        for (Instruction &i: bb) {

          if (auto uid_md = i.getMetadata("__PMC_UniqueID")) {
            if (auto *uid_cmd = llvm::dyn_cast<llvm::ConstantAsMetadata>(uid_md->getOperand(0))) {
              auto *uid_const = llvm::dyn_cast<llvm::ConstantInt>(uid_cmd->getValue());
              if (uid_const) {
                int64_t uid_int = uid_const->getSExtValue();
                InstToIDMap[&i] = uid_int;
              }
            }
          }
          
          if (auto dbgloc = i.getDebugLoc()) {
            DISubprogram *subprogram = getDISubprogram(i.getDebugLoc().getScope());
            auto subname = subprogram->getName().str();
            InstToSubProgramName[&i] = subname;
          }
          
        }
      }
    }

  void insertFence(Function &F) {
    LLVMContext &Context = F.getContext();
    IRBuilder<> Builder(Context);
    FunctionType *FenceFuncType = FunctionType::get(Type::getVoidTy(Context), //{VoidPtrTy}, false); 
                                                    {Type::getInt32Ty(Context),
                                                    Type::getInt32Ty(Context)}, false);
    FunctionCallee FenceFunc = F.getParent()->getOrInsertFunction("__fence", FenceFuncType);

    for (BasicBlock &BB : F) {
      for (Instruction &I : BB) {
        if (CallInst *callInst = dyn_cast<CallInst>(&I)) {
	        if (const Function *calledFunc = callInst->getCalledFunction()) {
		        Function *parentFunc = callInst->getFunction();
            if (calledFunc->getName().find("fence")!=std::string::npos && parentFunc->getName().find("clflush")==std::string::npos) {
                llvm::Constant *LineLoc, *ColLoc;
                llvm::outs() << "Fence:" << I.getDebugLoc().get()<<", "<<parentFunc->getName()<<", "<<calledFunc->getName()<<"\n";
                if (I.getDebugLoc().get() != nullptr) {
                  LineLoc = llvm::ConstantInt::get(i32_type, I.getDebugLoc().getLine());
                  ColLoc = llvm::ConstantInt::get(i32_type, I.getDebugLoc().getCol());
                }
                else {
                  LineLoc = llvm::ConstantInt::get(i32_type, 0);
                  ColLoc = llvm::ConstantInt::get(i32_type, 0);
                }
                Builder.SetInsertPoint(&I);
                Builder.CreateCall(FenceFunc, {LineLoc, ColLoc});
            }
          }          
        }
      }
    }
  }

  void insertFlush(Function &F) {
	
    LLVMContext &Context = F.getContext();
    IRBuilder<> Builder(Context);
	
	  Type *VoidPtrTy = Type::getInt8PtrTy(Context);
    FunctionType *FlushFuncType = FunctionType::get(Type::getVoidTy(Context), //{VoidPtrTy}, false); 
                                                    {Type::getInt8PtrTy(Context), 
                                                    Type::getInt64Ty(Context),Type::getInt32Ty(Context),
                                                    Type::getInt32Ty(Context)}, false);
    FunctionCallee FlushFunc = F.getParent()->getOrInsertFunction("__flush", FlushFuncType);

    for (BasicBlock &BB : F) {
      for (Instruction &I : BB) {

        if (CallInst *callInst = dyn_cast<CallInst>(&I)) {
	        if (const Function *calledFunc = callInst->getCalledFunction()) {
            if (calledFunc->getName().find("clflush")!=std::string::npos || 
                calledFunc->getName().find("simuFlushOpt")!=std::string::npos) {

                Value *argData = callInst->getArgOperand(0); 
                Value *argLen = callInst->getArgOperand(1); 
                llvm::Type *type = argLen->getType();
    
                // Print the type in a human-readable format
                llvm::outs() << "Type of argLen: ";
                type->print(llvm::outs());  // Print the type
                llvm::outs() << "\n";

                unsigned bitWidth = argLen->getType()->getIntegerBitWidth();
                Value *argLen64;
			          if (bitWidth == 64) {
                    argLen64 = argLen;  
                }
                if (bitWidth < 64) {
                    argLen64 = Builder.CreateZExtOrBitCast(argLen, llvm::Type::getInt64Ty(Builder.getContext()));
                }
                        
                llvm::Constant *LineLoc, *ColLoc;
                if (I.getDebugLoc().get() != nullptr) {
                  LineLoc = llvm::ConstantInt::get(i32_type, I.getDebugLoc().getLine());
                  ColLoc = llvm::ConstantInt::get(i32_type, I.getDebugLoc().getCol());
                }
                else {
                  LineLoc = llvm::ConstantInt::get(i32_type, 0);
                  ColLoc = llvm::ConstantInt::get(i32_type, 0);
                }
                Builder.SetInsertPoint(&I);
                // outs() << argLen64;
                Builder.CreateCall(FlushFunc, {argData, argLen64, LineLoc, ColLoc});
            }
          }          
        }
      }
    }
}
       
    void InstruDepMap(Function &F) {
      
      IRBuilder<> builder(F.getContext());
      BasicBlock *entryBB = BasicBlock::Create(F.getParent()->getContext(), "entry", &F, &F.front());
      builder.SetInsertPoint(entryBB);
      builder.SetCurrentDebugLocation(DebugLoc());

      // MemoryControlDepMap has pairs of the form (dep, [control, control, ...])
      for (auto const &pair: MemoryControlDepMap) {
        int dep = InstToIDMap[pair.first];
        for (auto const &i: pair.second) {
          int control = InstToIDMap[i];
          
          auto *dep_const = llvm::ConstantInt::get(i32_type, dep);
          auto *control_const = llvm::ConstantInt::get(i32_type, control);
          Value *args[] = {control_const, dep_const};
          builder.CreateCall(__pmc_depAdd, args);
        }
      }

      // DataDepMap has pairs of the form (dep, [control, control, ...])
      for (auto const &pair: DataDepMap) {
        int dep = InstToIDMap[pair.first];
        for (auto const &i: pair.second) {
          int control = InstToIDMap[i];
          auto *dep_const = llvm::ConstantInt::get(i32_type, dep);
          auto *control_const = llvm::ConstantInt::get(i32_type, control);
          Value *args[] = {control_const, dep_const};
          builder.CreateCall(__pmc_depAdd, args);
        }
      }
      builder.CreateBr(F.begin()->getNextNode());
    }

    void visitCallInst(CallInst &CALLI) {
      // do nothing
    }

    void visitLoadInst(LoadInst &LI) {
      if (auto *gv = dyn_cast<GlobalVariable>(LI.getOperand(0))) {
	      return;
      }
      auto &I = cast<Instruction>(LI);

      Value *ptr = LI.getPointerOperand();
      Value *loaded = LI.getOperand(0);

      // Check loading pmem_(c)alloc
      if (ptr->hasName()) {
        if (ptr->getName().contains("pmem_calloc")) {
          //InstruPmemCalloc(LI);
          assert(0); //chao: when does this occur?
        }
        else if (ptr->getName().contains("pmem_free")) {
          //InstruPmemFree(LI);
          assert(0); //chao: when does this occur?
        }
      }
      
      // Address printed only if it is in PM
      InstruAddr(I);
    }

    void visitStoreInst(StoreInst &SI) {
      // Skip global counter instrumentation
      //outs()<<"Visiting store instruction for: "<<I<<"\n";
      if (auto *gv = dyn_cast<GlobalVariable>(SI.getOperand(1))) {
        if (gv->getName() == "Inst_Counter") {
          return;
        }
      }

      auto &I = cast<Instruction>(SI);
      Value *v = getPointerOperand(&I);

      // Address printed only if it is in PM
      InstruAddr(I);
    }

    /*
    // Store the address of the pmem alloc corresponding store's address
    void InstruPmemAlloc(StoreInst &I) {
      IRBuilder<> builder(I.getContext());
      builder.SetInsertPoint(&I);
      builder.SetCurrentDebugLocation(I.getDebugLoc());
      Value *stored = I.getValueOperand();
      LLVM_DEBUG(dbgs() << *stored << " type : " << *stored->getType() << " pointer type : "
		 << *stored->getType()->getPointerElementType() << "\n");
      // We only care about the address of the stored, since it will be store in PM
      Value *stored_i64 = builder.CreatePtrToInt(stored, i64_type);
    }

    // Store the address of the pmem alloc corresponding store's address
    void InstruPmemCalloc(LoadInst &LI) {
      DataLayout DL = LI.getFunction()->getParent()->getDataLayout();
      for (Use &U: LI.uses()) {
	auto *user = cast<Instruction>(U.getUser());
	// Process the user instruction
	if (auto *CI = dyn_cast<CallInst>(user)) {
	  IRBuilder<> builder(CI->getContext());
	  auto *OP1 = CI->getOperand(0);
	  auto *OP2 = CI->getOperand(1);
	  Value *totalSize;
	  if (isa<ConstantInt>(OP1) && isa<ConstantInt>(OP2)) {
	    totalSize = builder.CreateMul(OP1, OP2);
	  }

	  for (Use &U_CI: CI->uses()) {
	    user = cast<Instruction>(U_CI.getUser());
	    if (auto *BCI = dyn_cast<BitCastInst>(user)) {
	      for (Use &U_BCI: BCI->uses()) {
		// Found Store Instruction stores data on PM
		// Since it is calloc, we need to
		user = cast<Instruction>(U_BCI.getUser());
		if (auto *SI = dyn_cast<StoreInst>(user)) {
		  builder.SetInsertPoint(SI);
		  builder.SetCurrentDebugLocation(SI->getDebugLoc());
		  Value *stored = SI->getValueOperand();
		  Value *stored_i64 = builder.CreatePtrToInt(stored, i64_type);
		  Value *args[] = {stored_i64, totalSize};
		  builder.CreateCall(__pmc_memAdd, args);
		}
	      }
	    }
	  }
	}
	else if (auto *SI = dyn_cast<StoreInst>(user)) {
	  IRBuilder<> builder(SI->getContext());
	  builder.SetInsertPoint(SI);
	  builder.SetCurrentDebugLocation(SI->getDebugLoc());
	  Value *stored = SI->getValueOperand();
	  Value *stored_i64 = builder.CreatePtrToInt(stored, i64_type);
	  Value *memoryPointer = SI->getPointerOperand();
	  PointerType *pointerType = cast<PointerType>(memoryPointer->getType());
	  int size = DL.getTypeStoreSize(pointerType->getPointerElementType());
	  Value *args[] = {stored_i64, llvm::ConstantInt::get(i64_type, size)};
	  builder.CreateCall(__pmc_memAdd, args);
	}
      }
      
    }

    void InstruPmemFree(LoadInst &LI) {
      IRBuilder<> builder(LI.getContext());
      
      for (Use &U: LI.uses()) {
	auto *user = cast<Instruction>(U.getUser());
	// Process the user instruction
	if (auto *CI = dyn_cast<CallInst>(user)) {
	  auto *freedPtr = CI->getOperand(0);
	  builder.SetInsertPoint(CI);
	  builder.SetCurrentDebugLocation(CI->getDebugLoc());
	  Value *freedPtr_i64 = builder.CreatePtrToInt(freedPtr, i64_type);
	  builder.CreateCall(__pmc_memRemove, freedPtr_i64);
	}
      }
    }
    */

    llvm::Constant * getOrCreateGlobalStringPtr(IRBuilder<> *builder,StringRef name) {
      static std::map<StringRef,llvm::Constant*> N2C;
      static std::map<StringRef,llvm::Constant*>::iterator N2C_it;
      N2C_it = N2C.find(name);
      llvm::Constant *sc;
      if (N2C_it != N2C.end()) {
        sc = N2C_it->second;
      } 
      else {
        sc = builder->CreateGlobalStringPtr(name);
        N2C [ name ]  = sc;
      }
      return sc;
    }
    
    void InstruAddr(Instruction &I) {
      outs()<< "\n\n"<<I.dump()<<"\n"<<I.getFunction()->getParent()->getName()<<"\n";
      outs()<<I.getFunction()->getName()<<"\n"<<isa<StoreInst>(&I)<<"\n";
      IRBuilder<> builder(I.getContext());
      DataLayout DL = I.getFunction()->getParent()->getDataLayout();
      Value *address;
      StoreInst *SI;
      LoadInst *LI;
      int size;
      
      if ((SI = dyn_cast<StoreInst>(&I))) {
        address = SI->getPointerOperand();
        Value *memoryPointer = SI->getPointerOperand();
        PointerType *pointerType = cast<PointerType>(memoryPointer->getType());
        size = DL.getTypeStoreSize(pointerType->getPointerElementType());
      }
      else if ((LI = dyn_cast<LoadInst>(&I))) {
        address = LI->getPointerOperand();
        Value *memoryPointer = LI->getPointerOperand();
        PointerType *pointerType = cast<PointerType>(memoryPointer->getType());
        size = DL.getTypeStoreSize(pointerType->getPointerElementType());
      }
      assert(address != nullptr);

            Type *ty = address->getType();
            builder.SetInsertPoint(&I);
            builder.SetCurrentDebugLocation(I.getDebugLoc());
            Value *address_i64;
            if (ty->isPointerTy()) {
                address_i64 = builder.CreatePtrToInt(address, i64_type);
            }
            else if (ty->isIntegerTy()) {
                address_i64 = builder.CreateIntCast(address, i64_type, 1);
            }
            else {
                assert(false && "Wrong Address Loading Type! Update LLVM Trace Gen Pass!");
            }

            llvm::Constant *i32_id = llvm::ConstantInt::get(i32_type, InstToIDMap[&I]/*value*/);
            llvm::Constant *i32_size = llvm::ConstantInt::get(i32_type, size);
            llvm::Constant *LineLoc, *ColLoc;

//            if (I.getNextNode()->getDebugLoc().get() != nullptr) {
            if (I.getDebugLoc().get() != nullptr) {
                LineLoc = llvm::ConstantInt::get(i32_type, I.getDebugLoc().getLine());
                ColLoc = llvm::ConstantInt::get(i32_type, I.getDebugLoc().getCol());
                cout()<<LineLoc<<":"<<ColLoc<<"\n";
            }
            else {
                LineLoc = llvm::ConstantInt::get(i32_type, 0);
                ColLoc = llvm::ConstantInt::get(i32_type, 0);
            }
//            llvm::Constant *ScopeConstant = ConstantDataArray::getString(I.getContext(), InstToSubProgramName[&I], true);

            //llvm::Constant *ScopeConstant = builder.CreateGlobalStringPtr(StringRef(InstToSubProgramName[&I]));
            llvm::Constant *ScopeConstant = getOrCreateGlobalStringPtr(&builder, StringRef(InstToSubProgramName[&I]));

	    //            llvm::Constant *ScopeConstant = builder.CreateGlobalString(StringRef(InstToSubProgramName[&I]), "Test");
//            builder.Createstr
//            errs() << InstToSubProgramName[&I] << " " << InstToIDMap[&I] << "\n";

            // Get a pointer to the data array
//            llvm::Constant *StrPointer = ConstantExpr::getBitCast(StrConstant, Type::getInt8PtrTy(I.getContext()));

            llvm::ArrayRef< llvm::Value* > args = {address_i64, i32_size, i32_id, LineLoc, ColLoc, ScopeConstant};

            if (isa<LoadInst>(&I)) {
//                PrintedIDs.insert(InstToIDMap[&I]);
                builder.CreateCall(__pmc_printLoadAddr, args);
            }
            else if (isa<StoreInst>(&I)) {
//                PrintedIDs.insert(InstToIDMap[&I]);
                builder.CreateCall(__pmc_printStoreAddr, args);
            }
        }

    /*
        void InstruCountInstPrinter(Instruction &I) {
            IRBuilder<> builder(I.getContext());
            builder.SetInsertPoint(&I);
            GlobalValue *GV_ic = I.getModule()->getNamedGlobal("Inst_Counter");
            auto *load_inst_counter = builder.CreateLoad(GV_ic);
            builder.CreateCall(printCounter, load_inst_counter);
        }

        static void InstruCountInstExecuted(Instruction &I, unsigned inc) {
            // Step 0: create IR builder for I
            IRBuilder<> builder(I.getModule()->getContext());
            builder.SetInsertPoint(&I);

            // Step 1: instrument how many insts since last ld/store
            GlobalValue *GV_ic = I.getModule()->getNamedGlobal("Inst_Counter");
            ConstantInt *inc_const = ConstantInt::get(Type::getInt32Ty(I.getParent()->getParent()->getContext()),
                                                      inc);
            auto *load_inst_counter = builder.CreateLoad(GV_ic);
            auto *add_inst_counter = builder.CreateAdd(inc_const, load_inst_counter);
            auto *store_inst_counter = builder.CreateStore(add_inst_counter, GV_ic);
        }

        // Helper function to get the structs defined for debug
        void GetAllStructs(Function &F) {
            Module *M = F.getParent();
            const DataLayout &DL = M->getDataLayout();
            LLVM_DEBUG(dbgs() << "Store all structs in a .c file! \n");
            for (auto &ST: M->getIdentifiedStructTypes()) {
                if (!ST->isSized()) continue;
                LLVM_DEBUG(
                        dbgs() << "Struct: " << ST->getName() << "\t\tsize: " << DL.getTypeAllocSize(ST) << "\n");
                StTypeToSize[ST] = DL.getTypeAllocSize(ST);
                if (!ST->isLiteral()) {
                    std::string struct_name = ST->getName().str();
                    std::vector<Type *> fields;
                    for (unsigned i = 0; i < ST->getNumElements(); i++) {
                        fields.push_back(ST->getElementType(i));
                    }
                    StructFields[struct_name] = fields;
                }
            }
            for (auto [struct_name, fields]: StructFields) {
                LLVM_DEBUG(dbgs() << "Struct: " << struct_name << "\nFields: ");
                for (auto field: fields) {
                    LLVM_DEBUG(dbgs() << *field << ", ");
                }
                LLVM_DEBUG(dbgs() << "\n");
            }

            std::ofstream outfile(StructFieldsPath.c_str());
            for (const auto &pair: StructFields) {
                for (const auto &s: pair.second) outfile << s << " ";
                outfile << pair.first.c_str() << "\n";
            }
            outfile.close();
        }
    */

    void SetInstUniqueID(Function &F) {
      for (BasicBlock &bb : F) {
	
      for (Instruction &i : bb) {
        
        llvm::Type* i32_type = llvm::IntegerType::getInt32Ty(F.getContext());
        llvm::Type* i64_type = llvm::IntegerType::getInt64Ty(F.getContext());
        unsigned IDKind = F.getContext().getMDKindID("__PMC_UniqueID");
        Metadata *IDNode = ConstantAsMetadata::get(ConstantInt::get(i32_type, uniqueID));
        MDNode *MD = MDNode::get(F.getContext(), IDNode);
        // Attach the metadata to the instruction
        i.setMetadata(IDKind, MD);
        
        uniqueID++;
      }
	
      }
    }

    void InsertDummyBeginEnd(Function &F) {
            LLVMContext &Context = F.getContext();
            IRBuilder<> Builder(Context); //F.getContext());

            // Create the function name and label metadata
            MDNode *FuncNameMetadata = MDNode::get(Context, MDString::get(Context, F.getName()));

            // Create the "begin" dummy instruction
            ConstantInt *BeginDummyValue = ConstantInt::get(Builder.getInt32Ty(), 0);
            FunctionType *BeginDummyFuncType = FunctionType::get(Builder.getVoidTy(), {Builder.getInt32Ty()}, false);
            FunctionCallee BeginDummyFunc = F.getParent()->getOrInsertFunction("__pmc_dummy_begin", BeginDummyFuncType);
            Instruction *BeginDummy = Builder.CreateCall(BeginDummyFunc, {BeginDummyValue});

            BeginDummy->setMetadata("__PMC_FunctionName", FuncNameMetadata);

            // Insert it at the beginning of the entry block
            BasicBlock &EntryBlock = F.getEntryBlock();
            EntryBlock.getInstList().push_front(BeginDummy);

            // Create the "end" dummy instruction
            ConstantInt *EndDummyValue = ConstantInt::get(Builder.getInt32Ty(), 0);
            FunctionType *EndDummyFuncType = FunctionType::get(Builder.getVoidTy(), {Builder.getInt32Ty()}, false);
            FunctionCallee EndDummyFunc = F.getParent()->getOrInsertFunction("__pmc_dummy_end", EndDummyFuncType);
            Instruction *EndDummy = Builder.CreateCall(EndDummyFunc, {EndDummyValue});
            EndDummy->setMetadata("__PMC_FunctionName", FuncNameMetadata);
            BasicBlock &ExitBlock = F.back();
            // Insert it at the end of the exit block
            if (ExitBlock.getTerminator() != nullptr)
                EndDummy->insertBefore(ExitBlock.getTerminator());
            else
                ExitBlock.getInstList().push_back(EndDummy);
    }  
     
    void getAnalysisUsage(AnalysisUsage &AU) const override{
                AU.setPreservesCFG();
                AU.addRequired<DependenceAnalysisWrapperPass>();
                AU.addRequired<DominanceFrontierWrapperPass>();
                AU.addRequired<DominatorTreeWrapperPass>();
                AU.addRequired<PostDominatorTreeWrapperPass>();
                AU.addRequired<BasicAAWrapperPass>();
                AU.addRequired<MemorySSAWrapperPass>();
    }

  };

    char PMTraceGen::ID = 0;
    static RegisterPass<PMTraceGen> X("pmtracegen", "Generate runtime trace for persistent memory accesses.");

}
#undef DEBUG_TYPE
