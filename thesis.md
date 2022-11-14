# Thesis

## Abstract

## Introduction

### Context and Background

In an increasingly digital world, cybersecurity has emerged as a crucial consideration for individuals, companies, and governments trying to protect their information, financial assets, and intellectual property. Of the many digital threats, various forms malware continue to pervade the digital landscape and thus remain a key concern for security analysts. One approach for combating malware involves attempting to deconstruct and reason about the malware itself. Understanding the functionality and behavior of malware samples may aid a security analyst in identifying methods to thwart or disable the malware's effects on a target system and similar systems.

Although simple in concept, the act of reverse engineering and reasoning about malware proves to be a steep challenge. The primary issue is that access to high-level malware source code is almost never available and, thus, any reasoning about the malware must be derived from the malware sample itself. Another issue is that malware authors often leverage obfuscation techniques to mask the intention and behavior of malware samples. To evade antivirus tools using signature-based detection, malware authors may employ techniques such as dead-code insertion, register reassignment, subroutine reordering, instruction substitution, code transposition, and code integration []. To complicate semantic binary code analysis of malware samples, malware authors may leverage compile-time strategies such as stripping and compiler optimizations []. Although we have discussed these obfuscation strategies in the context of malware, these techniques may be also leveraged by developers or companies attempting to dissuade binary code analysis of proprietary software.

Despite the challenge of binary code analysis, there exist many tools that attempt to glean high-level semantic information from binary code samples. A *disassembler* takes binary code as input and produces architecture-specific assembly code as output. Many challenges and considerations exist in the disassembly process - particularly for stripped binary code - such as discerning code from data and locating function boundaries []. One invariant in the disassembly process, however, is that the mapping from assembly instructions to binary instructions and vice-versa is always one-to-one. A *decompiler* takes this reverse mapping process one step further by translating binary code into an equivalent high-level source code representation. The decompilation process is inherently speculative since high-level information such as function boundaries, variables, data types, and high-level control flow mechanisms are lost when a program is compiled. With this, the decompiler must infer enough high-level structure for useful analysis without being overly aggressive and consequently blurring the program's intent. Many decompiler tools are currently in use by the reverse engineering community. Commercial decompiler tools include IDA Pro [] and JEB3 []. Popular open-source decompiler frameworks include Ghidra [], RetDec [], and Radare2 [].

### Problem and Motivation

Due to the number of decompiler tools as well as the imprecise nature of decompilation, a generalized and extensible quantitative evaluation framework for decompilers is critical but currently lacking in the literature. A standard evaluation framework for decompiler tools would allow analysts, researchers, and decompiler users and developers to objectively assess and compare decompilers against eachother or against a ground-truth. Ideally, evaluation could be performed at both the level of a single program and also over a set of benchmark programs via aggregate metrics. Evaluation at the single program level shall capture specific functions, variables, and data types that are missed, while analysis over a set of benchmarks would summarize key metrics extracted from the individual program evaluations.

### Research Objectives

Targeting the current gap in the literature discussed in the previous section, this paper presents a novel framework for quantifying and assessing the accuracy of decompiler tools. To prove our concept, we apply our framework to the Ghidra decompiler and subsequently discuss our findings. The primary objectives achieved by this work are as follows:

1. We define a domain-specific language (DSL), written in Python, for expressing high-level program information such as functions, variables, and data types. This is serves as a language-agnostic medium whereby we can translate program information extracted from a decompiler or a ground-truth source.
2. We extend our DSL to compare program information representations from different sources. A common use case is to compare ground-truth program information to decompiler-inferred program information.
3. Leveraging the comparison logic in (2), we define a set of quantitative metrics to measure the accuracy of function, variable, and data type inference.
4. We develop a translation module in Python that uses DWARF debugging information from a binary program to generate a ground-truth program information representation in our DSL.
5. We utilize the Ghidra Python API to implement a translation module, taking a Ghidra decompilation of a binary program as input and producing a program information representation in our DSL.
6. Using our developed language, metrics, and translation modules, we quantitatively assess the accuracy of the Ghidra decompiler when compared to ground-truth program information obtained from DWARF debugging information. We peform this analysis using the set of GNU Coreutils programs as benchmarks. We present the evaluation results and discuss additional findings and takeaways.

### Results Summary

### Contributions

### Paper Outline

The remainder of this paper is outlined as follows: In section 2, we discuss related research and background concepts useful for the understanding of this work. Next, in section 3, we detail our methodology for developing our evaluation framework. In section 4, we present and discuss our results of applying our evaluation framework to the Ghidra decompiler. We conclude in section 5 with a summary of our results, implications of our work, limitations, and future research directions.

## Background

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

*DWARF* is a debugging file format used by many compilers and debuggers to support source-level debugging for compiled binary programs []. When specified flags (usually '-g') are present at compilation, DWARF-supporting compilers such as GCC and Clang will write DWARF debugging information to an output binary program or object file. A resulting binary executable can then be loaded into a DWARF-supporting debugger such as GDB to debug the target binary program with references to line numbers, functions, variables, and types in the source-level program. The DWARF standard is source language agnostic, but generally supports equivalent representations for constructs present in common procedural languages such as C, C++, and Fortran. In addition, DWARF is decoupled from any architecture, processor, or operating system. The generalizability of DWARF debugging information makes it a prime candidate for extracting "ground-truth" information about a particular binary program, regardless of the specifics of the source language, architecture, processor, or operating system. DWARF is leveraged in this work to scrape ground-truth information about target binary programs. This information is subsequently used to evaluate the accuracy of the output produced by a target decompiler.

### Ghidra Reverse Engineering Framework

*Ghidra*, created and maintained by the National Security Agency Research Directorate, is an extensible software reverse engineering framework that features a disassembler, decompiler, and an integrated scripting environment in both Python and Java []. We use the Ghidra decompiler in this work to demonstrate our decompiler evaluation framework.

#### Ghidra Decompilation

### Related Work

## Methodology

In this section, we discuss the design, construction, and evolution of our decompiler evaluation framework. To achieve this, we identify key objectives that we subsequently address in more detail in the following subsections. These objectives are as follows:

1. Express program information such as functions, variables, data types, and addresses in a common representation.
2. Programmatically capture a "ground truth" representation for a given program.
3. Programmatically scrape program information from decompiler tools, namely Ghidra.
4. Compare two program representations of the same program.
5. Formulate quantitative metrics for evaluating the accuracy of a decompiler based on the comparison above.

### Domain-Specific Language (DSL) for Program Information

In order to make our framework general and reusable, we needed to devise a common domain-specific language (DSL) to represent program information such as functions, variables, data types, and addresses, as well as the relationships between them. This DSL must act as a bridge linking binary-level address information with the source-level structures such as functions, variables, and data types. Combining the information from these two layers of abstraction is, in essence, a mapping between binary-level and source-level structures. The accuracy of this mapping for a given decompiler is precisely the objective of our analysis.

[Figure representing how DSL can be constructed from many sources (DWARF, Ghidra, IDA Pro, etc.)]

The DSL we devised is entirely decoupled from the source of the program information. This allows any ground truth or decompiler source of program information to be translated into this common language and subsequently analyzed or compared with another source of program information. The core of our language is defined in Python and is compatible with Python (Jython or CPython) versions >= 2.7. We chose Python because the Ghidra framework supports custom Python scripts for querying and manipulating program information obtained from the disassembler and decompiler. In addition, the Python 'pyelftools' library [] allows scraping DWARF debugging information directly from binary programs. This DWARF information can then be utilized to construct a "ground truth" representation of program information. We will discuss this further in the next section.

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

The second, more favorable, approach to extracting ground truth program information involves leveraging debugging information optionally included in the binary by the compiler. The primary purpose of debugging information is to link binary-level instructions and addresses with source-level structures. This binary-level to source-level association is precisely what is needed to translate program information into our DSL. Since our framework is developed and targeted at Linux, we chose the DWARF debugging standard as the assumed debugging format for our framework. However, defining a translation module from another debugging format into our DSL is certainly possible and is an idea for future work. The DWARF debugging standard is supported by nearly all popular compilers and supports any source programming language (with possible extensions). These properties of the DWARF standard allow it to be used as a "ground truth" source of program information, decoupled from the source language or the compiler.

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

The strategy employed for the Ghidra translation is similar to that of our DWARF translation algorithm described in the previous section. We utilize functions exposed by the Ghidra API to obtain particular information about functions, variables, data types, and associated addresses gathered during the decompilation. We use the same IR defined for the DWARF translation to accumulate flattened records corresponding to these program constructs in a database. From here, we run the same resolution algorithm on the IR constructs database to generate the root *ProgramInfo* object in our DSL. The Ghidra-specific translation logic is implemented in roughly 900 lines of Python code.

### Comparison of "Ground Truth" and Decompiler Program Information

After converting both the ground-truth and decompiler program information into our DSL representation, we next formulate and implement a strategy to compare the two resulting *ProgramInfo* objects. To achieve this, we create an extension of our DSL that defines data structures and functions for capturing comparison information at different "levels of comparison". We discuss the specifics of these comparison levels in greater detail below.



### Quantitative Evaluation Metrics

## Results and Discussion

## Conclusion

### Summary of Results

### Limitations

### Future Work

## References
