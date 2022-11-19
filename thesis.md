# A Framework for Assessing Decompiler Inference Accuracy of Source-Level Program Constructs

## Abstract

Decompilation is the process of reverse engineering a binary program into an equivalent source code representation with the objective to recover high-level program constructs such as functions, variables, data types, and control flow mechanisms. Decompilation is applicable in many contexts, particularly for security analysts attempting to decipher the construction and behavior of malware samples. However, due to the loss of information during compilation, this process is naturally speculative and thus is prone to inaccuracy. This inherent speculation motivates the idea of an evaluation framework for decompilers.

In this work, we present a novel framework to quantitatively evaluate the inference accuracy of decompilers, regarding functions, variables, and data types. Within our framework, we develop a domain-specific language (DSL) for representing such program information from any "ground truth" or decompiler source. Using our DSL, we implement a strategy for comparing ground truth and decompiler representations of the same program. Subsequently, we extract and present insightful metrics illustrating the accuracy of decompiler inference regarding functions, variables, and data types, over a given set of benchmark programs. We leverage our framework to assess the correctness of the Ghidra decompiler when compared to ground truth information scraped from DWARF debugging information. We perform this assessment over a subset of the GNU Core Utilities (Coreutils) programs and discuss our findings.

## Introduction

### Context and Background

In an increasingly digital world, cybersecurity has emerged as a crucial consideration for individuals, companies, and governments trying to protect their information, financial assets, and intellectual property. Of the many digital threats, various forms malware continue to pervade the digital landscape and thus remain a key concern for security analysts. One approach for combating malware involves attempting to deconstruct and reason about the malware itself. Understanding the functionality and behavior of malware samples may aid a security analyst in identifying methods to thwart or disable the malware's effects on a target system and similar systems.

Although simple in concept, the act of reverse engineering and reasoning about malware proves to be a steep challenge. The primary issue is that access to high-level malware source code is almost never available and, thus, any reasoning about the malware must be derived from the malware sample itself. Another issue is that malware authors often leverage obfuscation techniques to mask the intention and behavior of malware samples. To evade antivirus tools using signature-based detection, malware authors may employ techniques such as dead-code insertion, register reassignment, subroutine reordering, instruction substitution, code transposition, and code integration []. To complicate semantic binary code analysis of malware samples, malware authors may leverage compile-time strategies such as stripping and compiler optimizations []. Although we have discussed these obfuscation strategies in the context of malware, these techniques may be also leveraged by developers or companies attempting to dissuade binary code analysis of proprietary software.

Despite the challenge of binary code analysis, there exist many tools that attempt to glean high-level semantic information from binary code samples. A *disassembler* takes binary code as input and produces architecture-specific assembly code as output. Many challenges and considerations exist in the disassembly process - particularly for stripped binary code - such as discerning code from data and locating function boundaries []. One invariant in the disassembly process, however, is that the mapping from assembly instructions to binary instructions and vice-versa is always one-to-one. A *decompiler* takes this reverse mapping process one step further by translating binary code into an equivalent high-level source code representation. The decompilation process is inherently speculative since high-level information such as function boundaries, variables, data types, and high-level control flow mechanisms are lost when a program is compiled. With this, the decompiler must infer enough high-level structure for useful analysis without being overly aggressive and consequently blurring the program's intent. Many decompiler tools are currently in use by the reverse engineering community. Commercial decompiler tools include IDA Pro [] and JEB3 []. Popular open-source decompiler frameworks include Ghidra [], RetDec [], and Radare2 [].

### Problem

Due to the number of decompiler tools as well as the imprecise nature of decompilation, a generalized and extensible quantitative evaluation framework for decompilers is critical. Existing work by Liu and Wang [] proposes an evaluation technique to determine whether recompiled decompiled programs are consistent in behavior to their original binaries. This technique, although useful, does not offer any insight into the inference accuracy of decompilers with respect to high-level program constructs such as functions, variables, and data types. The inference accuracy of the these high-level constructs are important for analysts to gain an understanding of the analyzed program.

### Research Objectives

Targeting the current gap in the literature outlined in the previous section, this paper presents a novel framework for quantifying and assessing the accuracy of decompiler tools. To prove our concept, we apply our framework to the Ghidra decompiler and subsequently discuss our findings. The primary objectives achieved by this work are as follows:

1. We define a domain-specific language (DSL), written in Python, for expressing high-level program information such as functions, variables, and data types. This is serves as a language-agnostic medium whereby we can translate program information extracted from a decompiler or a ground-truth source.
2. We extend our DSL to compare program information representations from different sources. A common use case is to compare ground-truth program information to decompiler-inferred program information.
3. Leveraging the comparison logic in (2), we define a set of quantitative metrics to measure the accuracy of function, variable, and data type inference.
4. We develop a translation module in Python that uses DWARF debugging information from a binary program to generate a ground-truth program information representation in our DSL.
5. We utilize the Ghidra Python API to implement a translation module, taking a Ghidra decompilation of a binary program as input and producing a program information representation in our DSL.
6. Using our developed language, metrics, and translation modules, we quantitatively assess the accuracy of the Ghidra decompiler when compared to ground-truth program information obtained from DWARF debugging information. We peform this analysis using the set of GNU Coreutils programs as benchmarks. We present the evaluation results and discuss additional findings and takeaways.

### Results Summary

### Contributions

### Outline

The remainder of this paper is outlined as follows: In section 2, we discuss related research and background concepts useful for the understanding of this work. Next, in section 3, we detail our methodology for developing our evaluation framework. In section 4, we present and discuss our results of applying our evaluation framework to the Ghidra decompiler. We conclude in section 5 with a summary of our results, implications of our work, limitations, and future research directions.

## Background & Related Work

### Software Reverse Engineering, Dissassembly, and Decompilation

*Software reverse engineering (SRE)* is the process of analyzing a software system with the intention to extract design and implementation information, particularly in situations where high-level source code is unavailable []. One common use case for this practice is to understand and deconstruct legacy code present in a software system where the source code has been lost. In this scenario, analysts could use SRE to understand this legacy code, determine its behavior, and ultimately decide how to reuse, patch, or replace the code. Another context for the use of SRE is computer security. Malware, or malicious programs, are nearly always present in binary form without their associated high-level source code. An analyst may use SRE to deconstruct the malware's logic, determine its behavior, and identify approaches to neutralize the malware and harden the host system for prevention of future attacks.

To perform SRE on a binary program, a critical first step is *disassembly*. This process takes binary code as input and produces assembly code as output. A key to this process is that binary and assembly instructions are always mapped one-to-one, and thus the main challenges lie in determining function boundaries and differentiating code, data, and metadata. Factors that contribute to these challenges include the following []:

* Data embedded in code regions
* Variable instruction size (on some architectures)
* Indirect branch instructions (the target of a branch instruction is not statically known)
* Functions without explicit `CALL` references
* Position independent code sequences
* Manually crafted assembly code

The conversion of binary code to assembly code through disassembly is a desirable starting point in the process of SRE. However, program semantics are still often difficult to interpret and reason about at the assembly code level. This difficulty necessitates an even more speculative process, *decompilation*, that takes a binary program as input and produces a high-level source code representation of the input program's semantics, usually in C. Decompilation, therefore, involves the speculative inference of high-level language concepts such as control flow mechanisms, variables, and data types. Decompiler tools rely heavily on the disassembly process as a first step in their analysis, and therefore the challenges affecting disassembly also naturally affect decompilation. Additional factors that obfuscate the accuracy of decompilation are the following:

* Compiler optimizations
* Stripped debugging information and metadata

With these compounding challenges affecting the decompilation process, it is clear that decompiler tools operate under a great degree of nondeterminism and speculation. This fact highlights the need for a common evaluation framework for decompiler tools.

<!-- ### Function, Variable, and Type Inference

Pertinent to both disassembly and decompilation, the inference of functions, variables, and data types are the key to insightful software reverse engineering. A vast amount of literature exists relating to algorithms for accurately inferring these source-level constructs from binary code. -->

### DWARF Debugging Standard

*DWARF* is a debugging file format used by many compilers and debuggers to support source-level debugging for compiled binary programs []. When specified flags (usually '-g') are present at compilation, DWARF-supporting compilers such as GCC and Clang will write DWARF debugging information to an output binary program or object file. A resulting binary executable can then be loaded into a DWARF-supporting debugger such as GDB to debug the target binary program with references to line numbers, functions, variables, and types in the source-level program. The DWARF standard is source language agnostic, but generally supports equivalent representations for constructs present in common procedural languages such as C, C++, and Fortran. In addition, DWARF is decoupled from any architecture, processor, or operating system. The generalizability of DWARF debugging information makes it a prime candidate for extracting "ground truth" information about a particular binary program, regardless of the specifics of the source language, architecture, processor, or operating system. DWARF is leveraged in this work to scrape ground-truth information about target binary programs. This information is subsequently used to evaluate the accuracy of the output produced by a target decompiler.

### Ghidra Reverse Engineering Framework

*Ghidra*, created and maintained by the National Security Agency Research Directorate, is an extensible software reverse engineering framework that features a disassembler, decompiler, and an integrated scripting environment in both Python and Java []. We use the Ghidra decompiler in this work to demonstrate our decompiler evaluation framework.

#### Ghidra Decompilation

### Related Work

In the 2020 paper *How Far We Have Come: Testing Decompilation Correctness of C Decompilers* by Liu and Wang [], the authors present an approach to determine the correctness of decompilers outputting C source code. They aim to find decompilation errors, recompilation errors, and behavior discrepancies exhibited by decompilers. To evaluate behavioral correctness, they attempt to recompile decompiled binaries (after potential syntax modifications) and use existing dynamic analysis techniques such as fuzzing to find differences in behavior between the recompiled and original programs. The objective of our work differs as we aim to evaluate decompiler inference of high-level structures such as functions, variables, and data types. Accurate inference of high-level structures enables easier understanding of decompiled programs by analysts; however, accurate behavior is also necessary to ensure that the decompiled representation is consistent with the original program. Hence, both of these works evaluate important aspects of decompiler correctness.

The review *Type Inference on Executables* by Caballero and Lin (2016) provides a comprehensive summary of recent literature on techniques used for variable discovery and type inference. In addition, the authors present various software reverse engineering (SRE) tools and frameworks in terms of their inputs, analysis types, output formats, and use cases. In essence, this work surveys the a set of decompiler tools and characterizes them based on their purported capabilities. The purpose of our work, on the contrary, is to objectively determine the correctness of decompiler tools based on their inference accuracy of high-level program constructs.

## Methodology

In this section, we discuss the design, construction, and evolution of our decompiler evaluation framework. To achieve this, we identify key objectives that we subsequently address in more detail in the following subsections. These objectives are as follows:

1. Express program information such as functions, variables, data types, and addresses in a common representation.
2. Programmatically capture a "ground truth" representation for a given program.
3. Programmatically scrape program information from decompiler tools, namely Ghidra.
4. Compare two program representations of the same program.
5. Formulate quantitative metrics for evaluating the accuracy of a decompiler based on the comparison above.

### Domain-Specific Language (DSL) for Program Information

In order to make our framework general and reusable, we devise a common domain-specific language (DSL) to represent program information such as functions, variables, data types, and addresses, as well as the relationships between them. This DSL must act as a bridge linking binary-level address information with the source-level structures such as functions, variables, and data types. Combining the information from these two layers of abstraction is, in essence, a mapping between binary-level and source-level structures. The accuracy of this mapping for a given decompiler is precisely the objective of our analysis.

[Figure representing how DSL can be constructed from many sources (DWARF, Ghidra, IDA Pro, etc.)]

The DSL we devised is entirely decoupled from the source of the program information. This allows any ground truth or decompiler source of program information to be translated into this common language and subsequently analyzed or compared with another source of program information. The core of our language is defined in Python and is compatible with Python (Jython or CPython) versions >= 2.7. We chose Python because the Ghidra framework supports custom Python scripts for querying and manipulating program information obtained from the disassembler and decompiler. In addition, the Python 'pyelftools' open-source library [] allows scraping DWARF debugging information directly from binary programs. This DWARF information can then be utilized to construct a "ground truth" representation of program information. We will discuss this further in the next section.

#### DSL Definitions

In this section, we will briefly describe the structure and relationships of the major constructs that comprise our DSL.

At the root of our DSL is the *ProgramInfo* type. The fields of this type include a list of global variables (*Variable* objects) and a list of functions (*Function* objects).

The *Function* type holds information about a function such as the name, the start PC address (*Address* object), the end PC address (*Address* object), a list of parameters (*Variable* objects), a list of local non-parameter variables (*Variable* objects), and the return type (*DataType* object).

The *Variable* type contains information about a source-level global variable, local variable, or parameter. A variable has a name, a data type (*DataType* object), and a list of address "live ranges". We consider a live range (*AddressLiveRange* type) to be the association of a variable's storage address with the PC address range where the storage location is valid for the variable. This "live range" concept allows for the expression of source-level variables that map to multiple underlying storage locations throughout their lifetime. Multiple live ranges may be associated with a single variable when compiler optimizations are present.

The *Address* type represents any absolute or relative location referenced in a binary program. This could include a PC location, variable storage location, or a register. From an implementation perspective, *Address* is the base class with subclasses representing the different types of address constructions based on context. These *Address* subclasses include *AbsoluteAddress*, *RegisterAddress*, *RegisterOffsetAddress*, and *StackAddress*. Each address is associated with an *AddressRegion*. This type is used to manage ordering and comparison logic for addresses that fall within the same region.

The last main construct in our core DSL is *DataType*. This type is represents a source-level data type and is typically associated with a variable or a function return type. *DataType* is the base of a class hierarchy with subclasses representing particular data types. The subclasses include *DataTypeFunctionPrototype*, *DataTypeInt*, *DataTypeFloat*, *DataTypeUndefined*, *DataTypeVoid*, *DataTypePointer*, *DataTypeArray*, *DataTypeStruct*, *DataTypeUnion*. Although these defined types correspond to C-like data types, this language can easily be extended to support other data types present in other high-level programming languages. All data type objects contain a "size" field representing the number of bytes the given data type occupies in memory.

### Capturing "Ground Truth" Program Information

With our DSL defined, we need a reliable method to extract "ground truth" information from a program and translate this information into our DSL. This "ground truth" information is intended to be used in a comparison with the program information obtained from a decompiler. Our framework is meant for evaluation and therefore we assume that we have access to the source code of benchmark programs to be used for the evaluation. With this assumption, we consider two options for extracting program information from a given source program.

The first option for extracting ground truth information is to parse the source code's abstract syntax tree (AST) and then use this AST to manually extract functions, variables, and data types. There are two major issues with this approach. First, parsing source code to an AST assumes a particular source programming language which greatly reduces generality. Second, obtaining the AST alone does not offer any binary-level information that allows us to link binary-level addresses with the source-level structures.

The second, more favorable, approach to extracting ground truth program information involves leveraging debugging information optionally included in the binary by the compiler. The primary purpose of debugging information is to link binary-level instructions and addresses with source-level structures. This binary-level to source-level association is precisely what is needed to translate program information into our DSL. Since our framework is developed and targeted at Linux, we choose the DWARF debugging standard as the assumed debugging format for our framework. However, defining a translation module from another debugging format into our DSL is certainly possible and is an idea for future work. The DWARF debugging standard is supported by nearly all major Linux compilers and supports any source programming language (with possible extensions). These properties of the DWARF standard allow it to be used as a "ground truth" source of program information, decoupled from the source language or the compiler.

#### Translating DWARF to the DSL

Starting with a source-level program, we must perform the following steps to extract program information represented in our DSL. First, we compile the source program with the option to include debugging symbols. In our particular analysis we use the GCC compiler specifying the "-g" flag. Many other compilers also offer the option for compilation with the inclusion of DWARF debugging symbols. After we compile the program, we then extract the DWARF debugging information from the resulting binary. We utilize the 'pyelftools' Python library [] to perform this extraction. The extraction results in, among other information, a set of debugging information entries (DIEs). Together, these DIE records provide a description of source-level entities such as functions, variables, and data types in relation to low-level binary information such as PC addresses and storage locations. Each DIE contains the following important features:

* An *offset* uniquely identifying the DIE within its compilation unit. These offsets are how DIEs reference other DIEs.
* A *tag* representing the "class" of the DIE. Example tags include "DW_TAG_subprogram", "DW_TAG_variable", and "DW_TAG_base_type".
* A set of *attributes* specifying tag-specific properties of the DIE. Examples include "DW_AT_name", "DW_AT_size", and "DW_AT_type".

The translation process from the DIE graph into our DSL is, at its core, a process of forming a nested data structure (our DSL's *ProgramInfo* type) from a flattened one (a collection of DWARF DIEs). To tackle this translation, we first define an intermediate representation (IR) language that acts as a "flattened" analog to the constructs present in our DSL. Instead of each IR construct directly containing the fields of other constructs, they instead contain fields that reference the IDs of other constructs through a shared database. The responsibility of the database is to map unique IDs to the flattened constructs. When all the IR constructs have been inserted into the database, the database then recursively resolves the flattened IR structures into their associated DSL structures, starting from the root *ProgramInfoStub* object, the IR analog to the *ProgramInfo* DSL type. This process is complicated by the fact that some data types, particularly *struct* types, may be recursive or mutually recursive, ultimately creating a cycle in the reference resolver. To address this, we implemented a mechanism whereby each IR node is marked when it is visited. Future attempts to resolve the same IR construct return with the existing object being resolved instead of attempting to resolve the same reference again. With the IR defined and the resolution logic in place, we map the DWARF DIE objects into our "flattened" IR and construct the IR object database. When all the DIEs are processed and translated, we specify the *ProgramInfoStub* node as the root reference and then execute our resolver algorithm to recursively generate the *ProgramInfo* object and subobjects defined in our DSL. Our DWARF translation module consists of about 1000 lines of Python code. The IR and resolver logic adds an additional 600 lines of code.

[DWARF parsing figure: DIEs -> IR -> DSL]

### Capturing Decompiler Program Information

In addition to capturing a ground-truth program representation in our DSL, we must construct a DSL representation of the program information obtained from a decompiler we wish to evaluate. Depending on the decompiler and the structure of its output, this process may take many forms, often involving querying APIs exposed by the decompiler framework. In all cases however, this shall involve defining a translation module from the decompiler output to the structures defined in the DSL. Hence, our framework can be employed on any decompiler assuming a translation module implementation.

#### Translating Ghidra Decompiler Output to the DSL

For our analysis of the Ghidra decompiler, we utilize the Ghidra scripting API to programmatically scrape and process information about the decompilation of target binary programs. The Ghidra scripting environment exposes its own collection of data structures and functions from which we obtain our information. Since the Ghidra scripting environment supports Python, we directly import and leverage our "flattened" IR (described in the previous section) and our DSL constructs to carry out the translation.

The strategy employed for the Ghidra translation is similar to that of our DWARF translation algorithm described in the previous section. We utilize the Ghidra API to obtain particular information about functions, variables, data types, and associated addresses gathered during the decompilation. Of particular use to our translation logic is the *DecompInterface* object exposed by the Ghidra API. This interface supports decompiling functions one at a time. Information inferred by each function's decompilation is used to update Ghidra's internal representation of the program information. By decompiling each of the functions extracted from Ghidra's disassembly analysis, we attempt to form a complete decompiled interpretation of the entire input program.

We use the same IR defined for the DWARF translation to accumulate flattened records corresponding to these program constructs in a database. From here, we run the same resolution algorithm on the IR constructs database to generate the root *ProgramInfo* object in our DSL. The Ghidra-specific translation logic is implemented in roughly 900 lines of Python code.

### Comparison of "Ground Truth" and Decompiler Program Information

After converting both the ground-truth and decompiler program information into our DSL representation, we next formulate and implement a strategy to compare the two resulting *ProgramInfo* objects. To achieve this, we create an extension of our DSL that defines data structures and functions for capturing comparison information at different layers.

#### Data Type Comparison

Given two *DataType* objects and an offset between their start locations, we devise a method to capture nuanced information about the comparison of the data types.

##### Definitions

We define the *metatype* of a data type to be general "class" of the given data type. These metatypes include *INT*, *FLOAT*, *POINTER*, *ARRAY*, *STRUCT*, *UNION*, *UNDEFINED*, *VOID*, and *FUNCTION_PROTOTYPE*. We consider *INT*, *FLOAT*, *POINTER*, *UNDEFINED*, and *VOID* to be *primitive metatypes* since they cannot be decomposed further. *ARRAY*, *STRUCT*, and *UNION* are considered *complex metatypes* since these types are formed via the composition or aggregation of different members or subtypes. We consider the 'char' data type to be of the *INT* metatype with size equal to one byte.

[Figure: Ariste type lattice]

A *primitive type lattice* [] is used to hierarchially relate primitive data types based on their metatype, size, and signedness (if applicable). More general types are located higher in the lattice while more specific types are located closer to the leaves. A type lattice may be used to determine whether two primitive data types are equivalent or share a common parent type.

[Figure: Subset relationship example(s)]

We next define a *subset* relationship between two data types. For a given complex data type X and another data type Y with a given offset (possibly 0) between the location of X and Y in memory, Y is considered a *subset* type of X if Y is equivalent to a "portion" of X, consistent with the offset between X and Y. For example, if X is an array, any sub-array or element of X such that elements are aligned and the element types are equivalent to X is considered a subset of X. If X is a struct or union, any sub-struct or member with proper alignment and equal constituent elements is considered a subset of X.

##### Comparison Logic

Suppose we have two *DataType* objects X (ground truth) and Y (decompiler) with offset k from the start of X to the start of Y. The goal is to compute the *data type comparison level* for the given comparison. The possible values for the comparison level are as follows, from lowest equality to highest equality:

* *NO_MATCH*: No relationship could be found between X and Y.
* *SUBSET*: Y is a subset type of the complex type X.
* *PRIMITIVE_COMMON_ANCESTOR*: In the primitive type lattice, primitive types X and Y share a common ancestor type.
* *MATCH*: All properties of X and Y match including metatype, size, and subtypes (if applicable).

We first check the equality of X and Y. If X and Y are equal, we assign the *MATCH* comparison code. In the case that X and Y are both primitive types, we attempt to compute their shared ancestor in the primitive type lattice. If a common ancestor could be found, we assign *PRIMITIVE_COMMON_ANCESTOR*. If X is a complex type, we employ an algorithm to determine whether Y is a subset of X at offset k by recursively descending into constituent portions of X starting at offset k (sub-structs, sub-arrays, elements, members) and checking for equality with Y. If a subset relationship is found, we assign the *SUBSET* compare level. In all other cases, we assign the *NO_MATCH* compare level.

#### Variable Comparison

There are two main contexts where variable comparison occurs. The first context is at the top level, where the set of ground-truth global variables is compared to the set of decompiler global variables. The second context for variable comparison is within the context of a function when we compare parameters or local variables between the ground-truth and the decompiler. In either case, comparing sets of variables starts with the decomposition of each *Variable* object from the DSL into a set of *Varnode* objects in our extended DSL.

A *Varnode* ties a *Variable* to a specific storage location and the range of PC addresses indicating when variable lives at that location. The varnodes for a given variable are directly computed from the variable's live ranges discussed previously. In unoptimized binaries, it is always the case that a single *Variable* will decompose into a single *Varnode*.

With each variable decomposed into its associated varnodes, we next partition the varnodes from each the ground-truth and the decompiler based on the "address space" in which they reside. These address spaces include the *absolute* address space, the *stack* address space, and the *register offset* address space (for a given register). The *stack* address space is a special case of the *register offset* address space where the offset register is the base pointer which points to the base of the current stack frame.

For the set of varnodes in each address space, we first order them based on their offset within the address space. Next, we attempt to find overlaps between varnodes from the two sources based on their location and size. If an overlap occurs between two varnodes, we compute a data type comparison taking into account the offset between the start locations of the two varnodes. The data type comparison approach is described in the previous section.

Based on the overlap status and data type comparison of a ground-truth varnode X, one of the following *varnode comparison levels* will be assigned:

* *NO_MATCH*: X is not overlapped with any varnodes from the other source.
* *OVERLAP*: X overlaps with one or more varnodes from the other space, but the data type comparisons are level *NO_MATCH*.
* *SUBSET*: X overlaps with one or more varnodes and each of its compared varnodes has data type comparison level equal to *SUBSET*. In other words, the compared varnode(s) make up a portion of X.
* *ALIGNED*: For some varnode Y from the other source, X and Y share the same location and size in memory; however, the data types of X and Y do not match. The data types comparison could have any compare level less than *MATCH*.
* *MATCH*: For some varnode Y from the other source, X and Y share the same location and size in memory, and their data types match exactly.

##### Decomposed Variable Comparison

The inference of variables with complex data types including structs, arrays, and unions proves to be a major challenge for decompilers. Recognizing this, we develop an approach to compare the sets of ground truth and decompiler variables (varnodes) in their most "decomposed" forms. An analysis of this sort helps to recognize how well a decompiler infers the primitive constituent components of complex variables. Furthermore, this allows us to recognize the aggressiveness and accuracy of complex variable synthesis from more primitive components.

[Figure: Example of "decomposing" complex varnode]

We first implement an approach to recursively strip away the "complex layers" of a varnode to its most primitive decomposition. This primitive decomposition produces a set of one or more primitive varnodes. For example, an array of elements is broken down into a set of its elements (decomposed recursively). A struct is broken down into a set of varnodes associated with each of its members (decomposed recursively).

We apply this primitive decomposition to each varnode in the sets of ground truth and decompiler varnodes. With the two sets of decomposed varnodes, we leverage the same variable comparison approach described previously to compare the varnodes in these sets. The resulting comparison information is treated as a separate analysis from the unaltered varnode sets.

#### Function Comparison

The first step in function comparison is to determine whether each ground-truth function is found by the decompiler. We first order the functions from each source by the start PC address of the function. Next, we attempt to match the functions from the two sources based on start address. Any functions from the ground-truth that are not matched by a decompiler function are considered "missed". Functions the are found by the decompiler but absent from the ground-truth are considered "extraneous". For any missed functions, we consider its associated parameters, local variables, and data types to also be "missed".

For each "matched" function based on start PC address, we compute and store information including the return type comparison, parameter comparisons, and local variable comparisons. These sub-comparisons leverage the data type and variable comparison techniques described previously.

### Quantitative Evaluation Metrics

In this section, we define quantitative metrics for evaluating the accuracy of the a given decompiler when compared to a ground-truth source. We rely on the function, variable, and data type comparison information discussed previously to extract these metrics. In the following sub-sections, we define sets of metrics that associated with tables seen in our evaluation results section.

#### Data Bytes

These metrics look at the total number of data bytes from all variables recovered by the decompiler when compared to the ground-truth source.

* *Ground truth data bytes*: The total number of data bytes captured from the ground truth source, derived from all global and local variables.
* *Bytes found*: The total number of data bytes recovered by the decompiler that overlap with data bytes found in the ground truth.
* *Bytes missed*: The number of data bytes present in the ground truth that were not recovered by the decompiler.
* *Bytes recovery fraction*: The fraction of ground truth data bytes found by the decompiler divided by the total number of ground truth bytes.

#### Functions

This set of metrics outlines the function identification performance of the decompiler.

* *Ground truth functions*: The number of functions present in the ground truth program representation.
* *Functions found*: The number of functions from the ground truth set that are identified by the decompiler.
* *Functions missed*: The number of functions from the ground truth set that are not identified by the decompiler.
* *Functions recovery fraction*: The fraction of ground truth functions found by the decompiler divided by the number of ground truth functions.

#### Varnodes

Recall that a *Varnode* is defined to be a source-level *Variable* tied to a single storage location for a range of PC addresses. In analyses of unoptimized binaries, the mapping of variables to varnodes is one to one. This set of metrics illustrates the decompiler's accuracy in recovering varnodes.

* *Ground truth varnodes*: The total number of varnodes present in the ground truth source. This includes varnodes associated with global and local variables from all functions.
* *Varnodes matched @ level=LEVEL*: Each ground truth varnode is associated with a *varnode comparison level* (*NO_MATCH*, *OVERLAP*, *SUBSET*, *ALIGNED*, *MATCH*) during the comparison with the set of decompiler varnodes. This metric specifies the number of ground truth varnodes that are matched at the specified level.
* *Varnodes average comparison score*: For each *varnode comparison level*, we first linearly assign an integer representing the strength of the varnode comparison (*NO_MATCH* = 0, *OVERLAP* = 1, *SUBSET* = 2, *ALIGNED* = 3, *MATCH* = 4). We then normalize these scores to fall within the range zero to one. Then, for each ground truth varnode, we compute this normalized score. We take the average score over all ground truth varnodes to obtain the resulting metric. This metric approximates how well, on average, the decompiler infers the ground truth varnodes.

We repeat this varnode analysis for the decomposed (primitive) set of varnodes resulting from recursively decomposing each of the high-level varnodes into its most primitive set of varnodes. We also repeat our analysis of the original set of varnodes filtered by metatype. The metatypes considered are *INT*, *FLOAT*, *POINTER*, *ARRAY*, *STRUCT*, and *UNION*. Lastly, we repeat the analysis of the decomposed varnodes when filtered by metatype. For this metatype analysis over the decomposed varnodes, we only consider the primitive metatypes *INT*, *FLOAT*, and *POINTER* since the varnodes are guaranteed to be primitive.

#### Array Comparisons

In this set of metrics, we aim to evaluate the accuracy of the array inference performed by the decompiler. We examine each array comparison made during the comparison of the ground truth with the decompiler and observe the discrepancies in length, size (bytes), dimensions, and element type. The following metrics are presented:

* *Array comparisons*: The number of total array comparisons made when comparing the ground truth with the decompiler.
* *Array length (elements) average error*: For each array comparison, we find the absolute difference in the number of elements inferred by the decompiler as compared to the ground truth. We then average these differences over all array comparisons to arrive at this metric.
* *Array length (elements) average error ratio*: For each array comparison, we first find the absolute difference in the number of elements inferred by the decompiler as compared to the ground truth. We then divide this error by the length of the ground truth array to get the error as a ratio of the array size. The average of these ratios over all array comparisons produces this metric.
* *Array size (bytes) average error*: This metric is similar to *Array length (elements) average error* but measures the error in bytes instead of number of elements.
* *Array size (bytes) average error ratio*: This metric is similar to *Array length (elements) average error ratio* but computes the error in bytes instead of array elements.
* *Array dimension match score*: This metric is the number of array comparisons where the decompiler inferred the correct number of dimensions divided by the total number of array comparisons.
* *Array average element type comparison score*: Each *data type comparison level* is first mapped to an integer as follows: *NO_MATCH* = 0, *SUBSET* = 1, *PRIMITIVE_COMMON_ANCESTOR* = 2, *MATCH* = 3. We then normalize these values such that the range is scaled from 0 to 1. We refer to this as the *data type comparison score*. Then, for each array comparison, we compute the *data type comparison score* and subsequently average the scores across all array comparisons to generate this metric.

## Evaluation

To demonstrate our evaluation framework, we target the Ghidra decompiler (version 10.2). We use a subset of the GNU Coreutils (version 9.1) programs as our benchmarks. For each of the benchmark programs, we evaluate the accuracy of Ghidra decompilation with the program compiled in two ways: (1) stripped and (2) DWARF debug symbols included. We use the results from each of these cases to discern how the amount of information included in the binary affects the Ghidra decompiler's inference accuracy. To limit the scope of our analysis, we only consider unoptimized binaries. We use the GCC compiler (version 11.1.0) to compile the benchmark programs. The architecture and operating system of the testing machine are x86-64 and Ubuntu Linux (version 20.04), respectively.

### Setup

Prior to evaluation, we compile the 105 Coreutils benchmark programs with two compilation configurations: (1) stripped and (2) DWARF debug symbols included. For each program, we first extract the ground truth information from the binary with DWARF symbols included via our DWARF translation module. We then use our Ghidra translation module to extract the Ghidra decompilation information from the binaries compiled under the two compilation configurations. At this point, all program information from the DWARF and Ghidra sources are represented as *ProgramInfo* objects in our DSL.

Next, for each program, we perform a comparison of the program information scraped from DWARF (from the binary including DWARF symbols) with the information obtained from the Ghidra decompilation of the programs under both of the compilation configurations. The information from these comparisons are expressed in the form of objects which contain comparison information about functions, variables, and data types compared between the DWARF and Ghidra sources.

With the comparisons computed for each program and compilation configuration, we use these comparisons to compute high-level metrics that summarize the performance of the Ghidra decompiler with respect to both stripped and debug-enabled binaries.

### Results

For the clarity of our presentation and discussion, we select a subset of 13 Coreutils programs used in the KLEE paper [] (*stat*, *nohup*, *pinky*, *csplit*, *ginstall*, *fmt*, *df*, *join*, *expr*, *seq*, *unexpand*, *tsort*, *tee*, *base64*, *sum*) and include 2 programs, *cksum* and *wc*, in which the Ghidra decompiler produces interesting and anomalous results in terms of variable and data bytes recovery. Although the evaluation of only 15 benchmarks are discussed in this section, we have included the results for all 105 Coreutils benchmarks in the appendix.

#### Function Recovery

We first evaluate the Ghidra decompiler in terms of its ability to recover functions present in the ground truth.

[Table: FUNCTIONS (stripped)]
[Table: FUNCTIONS (debug)]

Upon performing our function recovery evaluations, we find that Ghidra recovers 100% functions across all of our 15 evaluated programs as well as the entire set of 105 Coreutils benchmark programs. This finding holds true in both the debug and stripped compilation cases. This is a promising result for the Ghidra decompiler.

#### Variable (Varnode) Recovery

##### High-Level Varnode Recovery

To evaluate the variable (varnode) recovery accuracy of the Ghidra decompiler, we first measure the inference performance of high-level varnodes, including varnodes with complex and aggregate types such as arrays, structs, and unions. We further measure the varnode inference accuracy by metatype to decipher which of the metatypes are most and least accurately inferred by the decompiler. This analysis is performed under both compilation configurations (stripped and debugged).

###### Stripped

[Table: VARNODES (stripped)]

Table XX shows the a breakdown of the match level of each high-level varnode present in the ground truth when compared to varnodes inferred by the decompiler. We note that *NO_MATCH* indicates that no part of the ground truth varnode was recovered by the decompiler and thus refers to a miss.

avg comparison score = 80.8%
add column : fraction of varnodes partially recovered
average fraction of varnodes partially recovered = 98.5%
add column : fraction of varnodes exactly recovered
average fraction of varnodes exactly recovered = 37.7%

[Table: Metatype vs match level] - for each metatype, sum varnodes (across all programs) that match each match level

###### Debugged

[Table: VARNODES (debug)]

##### Decomposed Varnode Recovery

In this section, we repeat a similar varnode recovery analysis over all varnodes while first decomposing each varnode into its most primitive set of constituent varnodes (see section ...).

[Table: VARNODES (decomposed) (stripped)]
[Table: VARNODES (decomposed) (debug)]

#### Data Bytes Recovery

Following from our varnode inference analysis, we next assess the accuracy of the Ghidra decompiler in regards to the total number of data bytes recovered across all varnodes. This analysis provides an important perspective on data recovery, as the size of an improperly inferred varnode may result in a wide range in the number of misinferred bytes (e.g., a 1000-byte array versus a single character).

[Table: BYTES (debug)]
[Table: BYTES (stripped)]

#### Array Comparison Accuracy

### Discussion

## Conclusion

### Summary of Results

### Limitations

### Future Work

## References
