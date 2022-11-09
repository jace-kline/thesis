# Thesis

## Abstract

## Introduction

### Context and Background

In an increasingly digital world, cybersecurity has emerged as a crucial consideration for individuals, companies, and governments trying to protect their information, financial assets, and intellectual property. Of the many digital threats, various forms malware continue to pervade the digital landscape and thus remain a key concern for security analysts. One approach for combating malware involves attempting to deconstruct and reason about the malware itself. Understanding the functionality and behavior of malware samples may aid a security analyst in identifying methods to thwart or disable the malware's effects on a target system and similar systems.

Although simple in concept, the act of reverse engineering and reasoning about malware proves to be a steep challenge. The primary issue is that access to high-level malware source code is almost never available and, thus, any reasoning about the malware must be derived from the malware sample itself. Another issue is that malware authors often leverage obfuscation techniques to mask the intention and behavior of malware samples. To evade antivirus tools using signature-based detection, malware authors may employ techniques such as dead-code insertion, register reassignment, subroutine reordering, instruction substitution, code transposition, and code integration []. To complicate semantic binary code analysis of malware samples, malware authors may leverage compile-time strategies such as stripping and compiler optimizations []. Although we have discussed these obfuscation strategies in the context of malware, these techniques may be also leveraged by developers or companies attempting to dissuade binary code analysis of proprietary software.

Despite the challenge of binary code analysis, there exist many tools that attempt to glean high-level semantic information from binary code samples. A *disassembler* takes binary code as input and produces architecture-specific assembly code as output. Many challenges and considerations exist in the disassembly process - particularly for stripped binary code - such as discerning code from data and locating function boundaries []. One invariant in the disassembly process, however, is that the mapping from assembly instructions to binary instructions and vice-versa is always one-to-one. A *decompiler* takes this reverse mapping process one step further by translating binary code into an equivalent high-level source code representation. The decompilation process is inherently speculative since high-level information such as function boundaries, variables, data types, and high-level control flow mechanisms are lost when a program is compiled. With this, the decompiler must infer enough high-level structure for useful analysis without being overly aggressive and consequently blurring the program's intent. Many decompiler tools are currently in use by the reverse engineering community. Commercial decompiler tools include IDA Pro [] and JEB3 []. Popular open-source decompiler frameworks include Ghidra [], RetDec [], and Radare2 [].

### Problem and Motivation

Due to the number of decompiler tools as well as the imprecise nature of decompilation, a generalized and extensible quantitative evaluation framework for decompilers is critical but currently lacking in the literature. A standard evaluation framework for decompiler tools would allow analysts, researchers, and decompiler users and developers to objectively assess and compare decompilers against eachother or against a ground-truth representation. Ideally, evaluation could be performed at both the level of a single program and also over a set of benchmark programs via aggregate metrics. Evaluation at the single program level shall capture specific functions, variables, and data types that are missed, while analysis over a set of benchmarks would summarize key metrics extracted from the individual program evaluations.

### Contributions

Targeting the current gap in the literature discussed in the previous section, this paper presents a novel framework for quantifying and assessing the accuracy of decompiler tools. To prove our concept, we apply our framework to the Ghidra decompiler and discuss our findings. The primary contributions of this work are as follows:

1. We define a common domain-specific language (DSL), written in Python, for expressing high-level program information such as functions, variables, and data types. This is serves as a language-agnostic medium whereby we can translate program information extracted from a decompiler or a ground-truth source.
2. We extend our DSL to compare program information representations from different sources. A common use case is to compare a ground-truth program representation to a decompiler-inferred program representation.
3. Leveraging the comparison logic in (2), we define a set of quantitative metrics to that measure the accuracy of function, variable, and data type inference.
4. We develop a translation module in Python that uses DWARF debugging information from a binary program to generate a ground-truth program information representation in our DSL.
5. We utilize the Ghidra Python API to implement a translation module, taking a Ghidra decompilation of a binary program as input and producing a program information representation in our DSL.
6. Using our developed language, metrics, and translation modules, we quantitatively assess the accuracy of the Ghidra decompiler when compared to ground-truth information obtained from DWARF debugging information. We peform this analysis using the set of GNU Coreutils programs as benchmarks. We present the evaluation results and discuss additional findings and takeaways.

### Results Summary

### Paper Outline

The remainder of this paper is outlined as follows: In section 2, we discuss related research and background concepts useful for the understanding of this work. Next, in section 3, we detail our methodology for developing our evaluation framework. In section 4, we present and discuss our results of applying our evaluation framework to the Ghidra decompiler. We conclude in section 5 with a summary of our results, implications of our work, limitations, and future research directions.

## Background

### Software Reverse Engineering, Dissassembly, and Decompilation

### Function, Variable, and Type Inference

### DWARF

### Ghidra Reverse Engineering Framework

### Related Work

## Methodology

## Results and Discussion

## Conclusion

### Summary of Results

### Limitations

### Future Work

## References

