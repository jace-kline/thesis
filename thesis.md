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
2. We extend our DSL to compare program information representations from different sources. A common use case is to compare a ground-truth program representation to a decompiler-inferred program representation.
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

### Function, Variable, and Type Inference

### DWARF Debugging Standard

*DWARF* is a debugging file format used by many compilers and debuggers to support source-level debugging for compiled binary programs []. When specified flags (usually '-g') are present at compilation, DWARF-supporting compilers such as GCC and Clang will write DWARF debugging information to an output binary program or object file. A resulting binary executable can then be loaded into a DWARF-supporting debugger such as GDB to debug the target binary program with references to line numbers, functions, variables, and types in the source-level program. The DWARF standard is source language agnostic, but generally supports equivalent representations for constructs present in common procedural languages such as C, C++, and Fortran. In addition, DWARF is decoupled from any architecture, processor, or operating system. The generalizability of DWARF debugging information makes it a prime candidate for extracting "ground-truth" information about a particular binary program, regardless of the specifics of the source language, architecture, processor, or operating system. DWARF is leveraged in this work to scrape ground-truth information about target binary programs. This information is subsequently used to evaluate the accuracy of the output produced by a target decompiler.

### Ghidra Reverse Engineering Framework

### Related Work

## Methodology

## Results and Discussion

## Conclusion

### Summary of Results

### Limitations

### Future Work

## References

