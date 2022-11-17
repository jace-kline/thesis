# This module is meant to be a place to define metrics/stats/etc
from statistics import mean
from typing import Callable
from lang import *
from compare_unoptimized import *
from cache import cache

class Metric(object):
    
    def __init__(
        self,

        # a more detailed string that can be used to display the metric
        display_name: str,

        # the function/callable that actually computes the value of the metric, given an UnoptimizedProgramCompare2 object
        compute: Callable, # UnoptimizedProgramInfoCompare2 -> Any
    ):
        self.display_name = display_name
        self.compute = compute

    def get_display_name(self) -> str:
        return self.display_name

    def get_compute_function(self) -> Callable:
        return self.compute

    def __call__(self, cmp: UnoptimizedProgramInfoCompare2) -> Any:
        return self.compute(cmp)

    # the metric should be uniquely identified by its computer function
    def __hash__(self) -> int:
        return hash(self.compute)

    def __str__(self) -> str:
        return "<Metric '{}'>".format(self.display_name)

    def __repr__(self) -> str:
        return self.__str__()

class MetricsGroup(object):
    def __init__(
        self,
        name: str,
        display_name: str,
        metrics: List[Metric] = None
    ):
        self.name = name
        self.display_name = display_name
        self.metrics = metrics if metrics is not None else []

    def get_name(self) -> str:
        return self.name

    def get_display_name(self) -> str:
        return self.display_name

    def get_metrics(self) -> List[Metric]:
        return self.metrics

    def add_metric(self, metric: Metric):
        self.metrics.append(metric)

    def mk_add_metric(self,
        display_name: str,
        compute: Callable # UnoptimizedProgramInfoCompare2 -> Any
    ):
        self.metrics.append(
            Metric(
                display_name,
                compute
            )
        )

    def compute_results(self, cmp: UnoptimizedProgramInfoCompare2) -> List[Any]:
        return [ metric(cmp) for metric in self.metrics ]

    def __iter__(self) -> Iterator[Metric]:
        return iter(self.metrics)

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return "<MetricsGroup {}>".format(self.name)

    def __repr__(self) -> str:
        return self.__str__()

def make_metrics() -> List[MetricsGroup]:

    metrics_groups: List[MetricsGroup] = []

    # Data bytes metrics
    bytes_group = MetricsGroup("bytes", "DATA BYTES")
    bytes_group.mk_add_metric(
        "Ground truth data bytes",
        bytes_truth
    )

    bytes_group.mk_add_metric(
        "Bytes found",
        bytes_found
    )

    bytes_group.mk_add_metric(
        "Bytes missed",
        bytes_missed
    )
    metrics_groups.append(bytes_group)

    # Function metrics
    functions_group = MetricsGroup("functions", "FUNCTIONS")
    functions_group.mk_add_metric(
        "Ground truth functions",
        lambda cmp: len(functions_truth(cmp))
    )

    functions_group.mk_add_metric(
        "Functions found",
        lambda cmp: len(functions_found(cmp))
    )

    functions_group.mk_add_metric(
        "Functions missed",
        lambda cmp: len(functions_missed(cmp))
    )
    metrics_groups.append(functions_group)

    # High-level Varnode metrics
    varnodes_group = MetricsGroup("varnodes", "VARNODES")
    varnodes_group.mk_add_metric(
        "Ground truth varnodes",
        lambda cmp: len(varnodes_truth(cmp))
    )

    for compare_level in VarnodeCompareLevel.range()[VarnodeCompareLevel.OVERLAP:]:
        compare_level_str = VarnodeCompareLevel.to_string(compare_level)
        varnodes_group.mk_add_metric(
            "Varnodes matched @ level={}".format(compare_level_str),
            lambda cmp, compare_level=compare_level: len(varnode_compare_records_matched_at_level(cmp, compare_level))
        )

    varnodes_group.mk_add_metric(
        "Varnode average comparison score [0,1]",
        varnodes_avg_compare_score
    )
    metrics_groups.append(varnodes_group)

    # MetaType-specific Varnode metrics
    for metatype in [MetaType.INT, MetaType.FLOAT, MetaType.POINTER, MetaType.ARRAY, MetaType.STRUCT, MetaType.UNION]:
        metatype_str = MetaType.repr(metatype)
        group = MetricsGroup(
            "varnodes_metatype_{}".format(metatype_str),
            "VARNODES (metatype = {})".format(metatype_str)
        )

        group.mk_add_metric(
            "Ground truth varnodes (metatype={})".format(metatype_str),
            lambda cmp, metatype=metatype: len(varnodes_truth_metatype(cmp, metatype))
        )

        for compare_level in VarnodeCompareLevel.range():
            compare_level_str = VarnodeCompareLevel.to_string(compare_level)
            group.mk_add_metric(
                "Decompiler varnodes matched @ level={} (metatype={})".format(compare_level_str, metatype_str),
                lambda cmp, metatype=metatype, compare_level=compare_level: len([
                    record for record in
                    varnode_compare_records_matched_at_level(cmp, compare_level)
                    if record.get_varnode().get_datatype().get_metatype() == metatype
                ])
            )

        group.mk_add_metric(
            "Varnode average compare score [0,1] (metatype={})".format(metatype_str),
            lambda cmp, metatype=metatype: varnodes_avg_compare_score_metatype(cmp, metatype)
        )
        metrics_groups.append(group)

    # Primitive Varnode metrics
    primitive_varnodes_group = MetricsGroup("varnodes_decomposed", "VARNODES (decomposed)")

    primitive_varnodes_group.mk_add_metric(
        "Ground truth varnodes (decomposed)",
        lambda cmp: len(varnodes_truth(cmp, primitive=True))
    )

    for compare_level in VarnodeCompareLevel.range():
        compare_level_str = VarnodeCompareLevel.to_string(compare_level)
        primitive_varnodes_group.mk_add_metric(
            "Varnodes matched @ level={} (decomposed)".format(compare_level_str),
            lambda cmp, compare_level=compare_level: len(varnode_compare_records_matched_at_level(cmp, compare_level, primitive=True))
        )

    primitive_varnodes_group.mk_add_metric(
        "Varnode average comparison score [0,1] (decomposed)",
        lambda cmp: varnodes_avg_compare_score(cmp, primitive=True)
    )
    metrics_groups.append(primitive_varnodes_group)

    # MetaType-specific primitive Varnode metrics
    for metatype in [MetaType.INT, MetaType.FLOAT, MetaType.POINTER]:
        metatype_str = MetaType.repr(metatype)
        group = MetricsGroup(
            "varnodes_decomposed_metatype_{}".format(metatype_str),
            "VARNODES (decomposed) (metatype = {})".format(metatype_str)
        )

        group.mk_add_metric(
            "Ground truth varnodes (decomposed) (metatype={})".format(metatype_str),
            lambda cmp, metatype=metatype: len(varnodes_truth_metatype(cmp, metatype, primitive=True))
        )

        for compare_level in VarnodeCompareLevel.range()[VarnodeCompareLevel.OVERLAP:]:
            compare_level_str = VarnodeCompareLevel.to_string(compare_level)
            group.mk_add_metric(
                "Varnodes matched @ level={} (decomposed) (metatype={})".format(compare_level_str, metatype_str),
                lambda cmp, metatype=metatype, compare_level=compare_level: len([
                    record for record in
                    varnode_compare_records_matched_at_level(cmp, compare_level, primitive=True)
                    if record.get_varnode().get_datatype().get_metatype() == metatype
                ])
            )

        group.mk_add_metric(
            "Varnode average compare score [0,1] (decomposed) (metatype={})".format(metatype_str),
            lambda cmp, metatype=metatype: varnodes_avg_compare_score_metatype(cmp, metatype, primitive=True)
        )
        metrics_groups.append(group)

    # Array comparison metrics
    array_group = MetricsGroup("array_comparisons", "ARRAY COMPARISONS")
    array_group.mk_add_metric(
        "Array comparisons",
        lambda cmp: len(array_comparisons(cmp))
    )

    array_group.mk_add_metric(
        "Array length (elements) average error",
        lambda cmp: mean_over_array_comparisons(cmp, array_elements_error)
    )

    array_group.mk_add_metric(
        "Array length (elements) average error ratio",
        lambda cmp: mean_over_array_comparisons(cmp, array_elements_error_ratio)
    )

    array_group.mk_add_metric(
        "Array size (bytes) average error",
        lambda cmp: mean_over_array_comparisons(cmp, array_size_error)
    )

    array_group.mk_add_metric(
        "Array size (bytes) average error ratio",
        lambda cmp: mean_over_array_comparisons(cmp, array_size_error_ratio)
    )

    array_group.mk_add_metric(
        "Array dimension match score [0,1]",
        array_dimension_match_ratio
    )

    array_group.mk_add_metric(
        "Array average element type comparison score [0,1]",
        array_subtype_avg_compare_score
    )
    metrics_groups.append(array_group)

    return metrics_groups

# Utility stuff / shared functions

# from a range, constructs a function that maps a member in that range
# to a number in continuous range [0,1]
def normalize_range(r: range) -> Callable:
    def inner(x) -> float:
        return None if x is None else (x - r.start) / (r.stop - r.step - r.start)
    return inner

def varnode_compare_level_to_normalized_score(lvl) -> float:
    return normalize_range(VarnodeCompareLevel.range())(lvl)

def datatype_compare_level_to_normalized_score(lvl) -> float:
    return normalize_range(DataTypeCompareLevel.range())(lvl)

# FunctionCompareRecord base filter
# return True if the function comparison is not None
def function_compare_record_compared_filter(fn_cmp: UnoptimizedFunctionCompareRecord) -> bool:
    return fn_cmp.is_comparison()

# Variable base filter
# variable is not a parameter & has single location associated with it
def variable_base_filter(var: Variable) -> bool:
    parent_fn = var.get_parent_function()
    return not var.is_param() \
        and var.is_single_loc()

# Varnode base filter
# varnode lives in a rangeable address region (stack, global, or register offset)
# & its parent variable matches the variable base filter
def varnode_base_filter(varnode: Varnode) -> bool:
    parent_var = varnode.get_var()
    return varnode.get_addr().get_region().is_range() \
        and (variable_base_filter(parent_var) if parent_var is not None else True)

# VarnodeCompareRecord base filter
# record's varnode satisfies the Varnode base filter
def varnode_compare_record_base_filter(record: VarnodeCompareRecord) -> bool:
    return varnode_base_filter(record.get_varnode())

# select all varnodes (possibly primitive) from either the left or right program info objects
# that satisfy the Varnode base filter
def select_base_varnodes(cmp: UnoptimizedProgramInfoCompare2, left: bool = True, primitive: bool = False) -> List[Varnode]:
    proginfo = cmp.get_left() if left else cmp.get_right()
    method = proginfo.select_primitive_varnodes if primitive else proginfo.select_varnodes
    return method(variable_cond=variable_base_filter, varnode_cond=varnode_base_filter)

# select all VarnodeCompareRecord objects (possibly primitive) from either the left or right program info objects
# that satisfy the VarnodeCompareRecord base filter
def select_base_varnode_compare_records(cmp: UnoptimizedProgramInfoCompare2, primitive: bool = False) -> List[VarnodeCompareRecord]:
    method = cmp.select_primitive_varnode_compare_records if primitive else cmp.select_varnode_compare_records
    return method(varnode_cmp_record_cond=varnode_compare_record_base_filter)

# select all VarnodeCompareRecord objects (possibly primitive) that match the base filters
# & contain a varnode that is either a global OR appears in a found/comparable function
@cache
def select_comparable_varnode_compare_records(cmp: UnoptimizedProgramInfoCompare2, primitive: bool = False) -> List[VarnodeCompareRecord]:
    method = cmp.select_primitive_varnode_compare_records if primitive else cmp.select_varnode_compare_records
    return method(
        function_cmp_record_cond=function_compare_record_compared_filter,
        varnode_cmp_record_cond=varnode_compare_record_base_filter
    )

# select all Varnode objects (possibly primitive) that match the base filters
# & are either globals OR appear in found functions
def select_comparable_varnodes(cmp: UnoptimizedProgramInfoCompare2, left: bool = True, primitive: bool = False) -> List[Varnode]:
    _cmp = cmp if left else cmp.flip()
    return [ record.get_varnode() for record in select_comparable_varnode_compare_records(_cmp, primitive=primitive) ]

# --------------------- BYTES --------------------------
# Ground-truth data bytes
def bytes_truth(cmp: UnoptimizedProgramInfoCompare2) -> int:
    return sum([ varnode.get_size() for varnode in varnodes_truth(cmp) ])

# Decompiler data bytes
def bytes_decomp(cmp: UnoptimizedProgramInfoCompare2) -> int:
    return sum([ varnode.get_size() for varnode in varnodes_decomp(cmp) ])

# Found bytes (in ground-truth & decompiler)
def bytes_found(cmp: UnoptimizedProgramInfoCompare2) -> int:
    return sum([ record.bytes_overlapped() for record in select_comparable_varnode_compare_records(cmp) ])

# Missed bytes (in ground-truth, not in decompiler)
def bytes_missed(cmp: UnoptimizedProgramInfoCompare2) -> int:
    return bytes_truth(cmp) - bytes_found(cmp)

# Extraneous bytes (in decompiler, not in ground-truth)
def bytes_extraneous(cmp: UnoptimizedProgramInfoCompare2) -> int:
    return bytes_decomp(cmp) - bytes_found(cmp)

# -------------------- FUNCTIONS -----------------------
# Ground-truth functions
def functions_truth(cmp: UnoptimizedProgramInfoCompare2) -> List[UnoptimizedFunction]:
    return list(cmp.get_left().get_unoptimized_functions().values())

# Decompiler functions
def functions_decomp(cmp: UnoptimizedProgramInfoCompare2) -> List[UnoptimizedFunction]:
    return list(cmp.get_right().get_unoptimized_functions().values())

# Found functions (in ground-truth & decompiler)
def functions_found(cmp: UnoptimizedProgramInfoCompare2) -> List[UnoptimizedFunction]:
    return [ record.get_unoptimized_function() for record in cmp.select_function_compare_records() if record.is_comparison() ]

# Missed functions (in ground-truth, not in decompiler)
def functions_missed(cmp: UnoptimizedProgramInfoCompare2) -> List[UnoptimizedFunction]:
    return [ record.get_unoptimized_function() for record in cmp.select_function_compare_records() if not record.is_comparison() ]

# Extraneous functions (in decompiler, not in ground-truth)
def functions_extraneous(cmp: UnoptimizedProgramInfoCompare2) -> List[UnoptimizedFunction]:
    return functions_missed(cmp.flip())

# ------------------ HIGH-LEVEL VARNODES -------------------
# Ground-truth high-level varnodes that are globals OR found in compared functions
def varnodes_truth(cmp: UnoptimizedProgramInfoCompare2, primitive: bool = False) -> List[Varnode]:
    return select_comparable_varnodes(cmp, left=True, primitive=primitive)

# Decompiler high-level varnodes that are globals OR found in compared functions
def varnodes_decomp(cmp: UnoptimizedProgramInfoCompare2, primitive: bool = False) -> List[Varnode]:
    return select_comparable_varnodes(cmp, left=False, primitive=primitive)

def varnode_compare_records_missed_(varnode_cmp_records: List[VarnodeCompareRecord]) -> List[VarnodeCompareRecord]:
    return _varnode_compare_records_match_levels(varnode_cmp_records, [VarnodeCompareLevel.NO_MATCH])

def varnodes_missed_(varnode_cmp_records: List[VarnodeCompareRecord]) -> List[Varnode]:
    return [ record.get_varnode() for record in varnode_compare_records_missed_(varnode_cmp_records) ]

# Missed high-level varnodes (ground-truth varnodes not compared with any decomp varnodes)
def varnodes_missed(cmp: UnoptimizedProgramInfoCompare2, primitive: bool = False) -> List[Varnode]:
    return [ record.get_varnode() for record in varnode_compare_records_match_levels(cmp, [VarnodeCompareLevel.NO_MATCH], primitive=primitive) ]

# Overlapped ground-truth high-level varnodes

def _varnode_compare_records_match_levels(varnode_cmp_records: List[VarnodeCompareRecord], levels: List[int]) -> List[VarnodeCompareRecord]:
    return [ record for record in varnode_cmp_records if record.get_compare_level() in levels ]

def _varnode_compare_records_matched_at_above_level(varnode_cmp_records: List[VarnodeCompareRecord], level: int) -> List[VarnodeCompareRecord]:
    return [ record for record in varnode_cmp_records if record.get_compare_level() >= level ]

def _varnode_compare_records_matched_at_level(varnode_cmp_records: List[VarnodeCompareRecord], level: int) -> List[VarnodeCompareRecord]:
    return [ record for record in varnode_cmp_records if record.get_compare_level() == level ]

# Ground-truth high-level varnodes matched @ or above <TAG>
def varnode_compare_records_match_levels(cmp: UnoptimizedProgramInfoCompare2, levels: List[int], primitive: bool = False) -> List[VarnodeCompareRecord]:
    return _varnode_compare_records_match_levels(select_comparable_varnode_compare_records(cmp, primitive=primitive), levels)

def varnode_compare_records_matched_at_above_level(cmp: UnoptimizedProgramInfoCompare2, level: int, primitive: bool = False) -> List[VarnodeCompareRecord]:
    return _varnode_compare_records_matched_at_above_level(select_comparable_varnode_compare_records(cmp, primitive=primitive), level)

def varnode_compare_records_matched_at_level(cmp: UnoptimizedProgramInfoCompare2, level: int, primitive: bool = False) -> List[VarnodeCompareRecord]:
    return _varnode_compare_records_matched_at_level(select_comparable_varnode_compare_records(cmp, primitive=primitive), level)

# Extraneous high-level varnodes (in decompiler, not overlapped with ground truth)
def varnodes_extraneous(cmp: UnoptimizedProgramInfoCompare2, primitive: bool = False) -> List[Varnode]:
    return varnodes_missed(cmp.flip(), primitive=primitive)

def _varnodes_avg_compare_level(varnode_cmp_records: List[VarnodeCompareRecord]) -> float:
    compare_levels = [ record.get_compare_level() for record in varnode_cmp_records ]
    return mean(compare_levels) if len(compare_levels) > 0 else None

# map each VarnodeCompareLevel into its integer encoding and find the average across all compare records
def varnodes_avg_compare_level(cmp: UnoptimizedProgramInfoCompare2, primitive: bool = False) -> float:
    return _varnodes_avg_compare_level(select_comparable_varnode_compare_records(cmp, primitive=primitive))

def varnodes_avg_compare_score(cmp: UnoptimizedProgramInfoCompare2, primitive: bool = False) -> float:
    return varnode_compare_level_to_normalized_score(varnodes_avg_compare_level(cmp, primitive=primitive))

# --------------- TYPE-SPECIFIC VARNODE COMPARISONS --------------------
def _select_comparable_varnodes_metatype(cmp: UnoptimizedProgramInfoCompare2, metatype: int, left: bool = True, primitive: bool = False) -> List[Varnode]:
    return [ varnode for varnode in select_comparable_varnodes(cmp, left=left, primitive=primitive) if varnode.get_datatype().get_metatype() == metatype ]

def _select_comparable_varnode_compare_records_metatype(cmp: UnoptimizedProgramInfoCompare2, metatype: int, primitive: bool = False) -> List[VarnodeCompareRecord]:
    return [ record for record in select_comparable_varnode_compare_records(cmp, primitive=primitive) if record.get_varnode().get_datatype().get_metatype() == metatype ]

# Ground-truth varnodes w/ metatype
def varnodes_truth_metatype(cmp: UnoptimizedProgramInfoCompare2, metatype: int, primitive: bool = False) -> List[Varnode]:
    return _select_comparable_varnodes_metatype(cmp, metatype, left=True, primitive=primitive)

# Decompiler varnodes w/ metatype
def varnodes_decomp_metatype(cmp: UnoptimizedProgramInfoCompare2, metatype: int, primitive: bool = False) -> List[Varnode]:
    return _select_comparable_varnodes_metatype(cmp, metatype, left=False, primitive=primitive)

def varnodes_missed_metatype(cmp: UnoptimizedProgramInfoCompare2, metatype: int, primitive: bool = False) -> List[Varnode]:
    return varnodes_missed_(_select_comparable_varnode_compare_records_metatype(cmp, metatype, primitive=primitive))

def _varnode_compare_records_matched_at_above_level_metatype(cmps: List[VarnodeCompareRecord], level: int, metatype: int, primitive: bool = False) -> List[VarnodeCompareRecord]:
    pass # return _varnode_compare_records_matched_at_above_level()

def varnode_compare_records_matched_at_above_level_metatype(cmp: UnoptimizedProgramInfoCompare2, level: int, metatype: int, primitive: bool = False) -> List[VarnodeCompareRecord]:
    pass

def varnodes_avg_compare_level_metatype(cmp: UnoptimizedProgramInfoCompare2, metatype: int, primitive: bool = False) -> float:
    return _varnodes_avg_compare_level(_select_comparable_varnode_compare_records_metatype(cmp, metatype, primitive=primitive))

def varnodes_avg_compare_score_metatype(cmp: UnoptimizedProgramInfoCompare2, metatype: int, primitive: bool = False) -> float:
    return varnode_compare_level_to_normalized_score(varnodes_avg_compare_level_metatype(cmp, metatype, primitive=primitive))

# Recovered ARRAY varnodes (in ground-truth & in decompiler - overlapped & same metatype)
@cache
def array_comparisons(cmp: UnoptimizedProgramInfoCompare2) -> List[VarnodeCompare2]:
    return cmp.select_varnode_comparisons(varnode_cmp_record_cond=varnode_compare_record_base_filter, varnode_cmp2_cond=lambda record: record.get_left().get_datatype().get_metatype() == MetaType.ARRAY and record.get_right().get_datatype().get_metatype() == MetaType.ARRAY)

# [VarnodeCompare2], (VarnodeCompare2 -> int|float) -> float
def _summarize_array_comparisons(cmps: List[VarnodeCompare2], f: Callable, stat: Callable = mean) -> float:
    return stat([ f(cmp2) for cmp2 in cmps ]) if cmps else None

# UnoptimizedProgramInfoCompare2, (VarnodeCompare2 -> int|float) -> float
def mean_over_array_comparisons(cmp: UnoptimizedProgramInfoCompare2, f: Callable) -> Callable:
    return _summarize_array_comparisons(array_comparisons(cmp), f, stat=mean)

## length inaccuracy (elements) of an array comparison
def array_elements_diff(cmp: VarnodeCompare2) -> int:
    return cmp.get_left().get_datatype().get_num_elements() - cmp.get_right().get_datatype().get_num_elements()

def array_elements_error(cmp: VarnodeCompare2) -> int:
    return abs(array_elements_diff(cmp))

## length inaccuracy ratio of an array comparison
def array_elements_error_ratio(cmp: VarnodeCompare2) -> float:
    return array_elements_error(cmp) / cmp.get_left().get_datatype().get_num_elements()

## size inaccuracy (bytes) of an array comparison
def array_size_diff(cmp: VarnodeCompare2) -> int:
    return cmp.get_left().get_size() - cmp.get_right().get_size()

def array_size_error(cmp: VarnodeCompare2) -> int:
    return abs(array_size_diff(cmp))

## size inaccuracy ratio of an array comparison
def array_size_error_ratio(cmp: VarnodeCompare2) -> float:
    return array_size_error(cmp) / cmp.get_left().get_size()

def _subtype_comparisons(cmps: List[VarnodeCompare2]) -> List[DataTypeCompare2]:
    def subtype_comparison(cmp: VarnodeCompare2) -> DataTypeCompare2:
        left_subtype = cmp.get_left().get_datatype().get_basetype()
        right_subtype = cmp.get_right().get_datatype().get_basetype()
        return DataTypeCompare2(left_subtype, right_subtype, 0)

    return [ subtype_comparison(cmp) for cmp in cmps ]

## subtype match % -> how many of the array comparisons had matching subtypes?
def _array_subtype_match_ratio(cmps: List[VarnodeCompare2], level: int = DataTypeCompareLevel.MATCH) -> float:
    subtype_matches = len([ cmp for cmp in _subtype_comparisons(cmps) if cmp.get_compare_level() >= level ])
    return subtype_matches / len(cmps)

def array_subtype_match_ratio(cmp: UnoptimizedProgramInfoCompare2, level: int = DataTypeCompareLevel.MATCH) -> float:
    return _array_subtype_match_ratio(array_comparisons(cmp), level=level)

def _array_subtype_avg_compare_level(cmps: List[VarnodeCompare2]) -> float:
    return mean([ cmp2.get_compare_level() for cmp2 in _subtype_comparisons(cmps) ]) if cmps else None

def array_subtype_avg_compare_level(cmp: UnoptimizedProgramInfoCompare2) -> float:
    return _array_subtype_avg_compare_level(array_comparisons(cmp))

def _array_subtype_avg_compare_score(cmps: List[VarnodeCompare2]) -> float:
    return datatype_compare_level_to_normalized_score(_array_subtype_avg_compare_level(cmps))

def array_subtype_avg_compare_score(cmp: UnoptimizedProgramInfoCompare2) -> float:
    return _array_subtype_avg_compare_score(array_comparisons(cmp))

## correct dimension % -> how many of the array comparisons had matching number of dimensions?
def _array_dimension_match_ratio(cmps: List[VarnodeCompare2]) -> float:
    dim_matches = 0
    for cmp in cmps:
        left_dims = cmp.get_left().get_datatype().num_dimensions()
        right_dims = cmp.get_right().get_datatype().num_dimensions()
        if left_dims == right_dims:
            dim_matches += 1

    return dim_matches / len(cmps) if len(cmps) > 0 else None

def array_dimension_match_ratio(cmp: UnoptimizedProgramInfoCompare2) -> float:
    return _array_dimension_match_ratio(array_comparisons(cmp))

# Recovered STRUCT varnodes (in ground-truth & in decompiler - overlapped & same metatype)
## average size inaccuracy (bytes)
## average size inaccuracy %
## average member type match %

# Ground-truth STRUCT varnodes matched @ or above <TAG>

# Extraneous STRUCT varnodes

def _mk_metrics(cmp: UnoptimizedProgramInfoCompare2) -> dict:
    METRICS = {
        "BYTES" : {
            "bytes - ground truth" : bytes_truth(cmp),
            "bytes - decompiler" : bytes_decomp(cmp),
            "bytes found" : bytes_found(cmp),
            "bytes missed" : bytes_missed(cmp),
            "bytes extraneous" : bytes_extraneous(cmp),
            "bytes found %" : 100.0 * (bytes_found(cmp) / bytes_truth(cmp))
        },
        "FUNCTIONS" : {
            "functions - ground truth" : len(functions_truth(cmp)),
            "functions - decompiler": len(functions_decomp(cmp)),
            "functions found" : len(functions_found(cmp)),
            "functions missed" : len(functions_missed(cmp)),
            "functions extraneous" : len(functions_extraneous(cmp)),
            "functions found %" : 100.0 * (len(functions_found(cmp)) / len(functions_truth(cmp)))
        },
    }

    varnodes_group = {}
    _varnodes_truth = len(varnodes_truth(cmp))
    varnodes_group["varnodes - ground truth"] = _varnodes_truth
    varnodes_group["varnodes - decompiler"] = len(varnodes_decomp(cmp))
    for level in range(VarnodeCompareLevel.NO_MATCH, VarnodeCompareLevel.MATCH + 1):
        varnodes_group["varnodes matched @ or above {}".format(VarnodeCompareLevel.to_string(level))] = len(varnode_compare_records_matched_at_above_level(cmp, level))
    varnodes_group["varnodes missed"] = len(varnodes_missed(cmp))
    varnodes_group["varnodes extraneous"] = len(varnodes_extraneous(cmp))
    varnodes_group["varnodes match %"] = 100.0 * (len(varnode_compare_records_matched_at_above_level(cmp, VarnodeCompareLevel.MATCH)) / _varnodes_truth)
    METRICS["VARNODES"] = varnodes_group

    primitives_group = {}
    _primitives_truth = len(varnodes_truth(cmp, primitive=True))
    primitives_group["primitive varnodes - ground truth"] = _primitives_truth
    primitives_group["primitive varnodes - decompiler"] = len(varnodes_decomp(cmp, primitive=True))
    for level in range(VarnodeCompareLevel.NO_MATCH, VarnodeCompareLevel.MATCH + 1):
        primitives_group["primitive varnodes matched @ or above {}".format(VarnodeCompareLevel.to_string(level))] = len(varnode_compare_records_matched_at_above_level(cmp, level, primitive=True))
    primitives_group["primitive varnodes missed"] = len(varnodes_missed(cmp, primitive=True))
    primitives_group["primitive varnodes extraneous"] = len(varnodes_extraneous(cmp, primitive=True))
    primitives_group["primitive varnodes match %"] = 100.0 * (len(varnode_compare_records_matched_at_above_level(cmp, VarnodeCompareLevel.MATCH, primitive=True)) / _primitives_truth)
    METRICS["PRIMITIVE VARNODES"] = primitives_group

    # parameters_group = {}
    # params_truth = cmp.get_left().select_varnodes(variable_cond=lambda var: var.is_param())
    # parameters_group["parameter varnodes - ground truth"] = params_truth
    # params_decomp = cmp.get_right().select_varnodes(variable_cond=lambda var: var.is_param())
    # parameters_group["parameter varnodes - decompiler"] = params_decomp
    # param_overlaps = cmp.select_varnode_compare_records(varnode_cmp_record_cond=lambda record: record.get_var() is not None and record.get_var().is_param() and record.get_compare_level() > VarnodeCompareLevel.NO_MATCH)
    # parameters_group["parameter overlaps"] = param_overlaps
    # METRICS["PARAMETER VARNODES"] = parameters_group

    for metatype in [MetaType.INT, MetaType.FLOAT, MetaType.POINTER, MetaType.ARRAY, MetaType.STRUCT, MetaType.UNION, MetaType.UNDEFINED]:
        metatype_group = {}
        truth = len(varnodes_truth_metatype(cmp, metatype))
        metatype_group["(metatype = {}) varnodes - ground truth".format(MetaType.repr(metatype))] = truth
        metatype_group["(metatype = {}) varnodes - decompiler".format(MetaType.repr(metatype))] = len(varnodes_decomp_metatype(cmp, metatype))
        metatype_group["(metatype = {}) varnodes missed".format(MetaType.repr(metatype))] = len([ record for record in varnode_compare_records_match_levels(cmp, [VarnodeCompareLevel.NO_MATCH]) if record.get_varnode().get_datatype().get_metatype() == metatype ])

        aligned = len([ record for record in varnode_compare_records_matched_at_above_level(cmp, VarnodeCompareLevel.ALIGNED) if record.get_varnode().get_datatype().get_metatype() == metatype ])
        metatype_group["(metatype = {}) varnodes matched @ or above ALIGNED".format(MetaType.repr(metatype))] = aligned

        matched = len([ record for record in varnode_compare_records_matched_at_above_level(cmp, VarnodeCompareLevel.MATCH) if record.get_varnode().get_datatype().get_metatype() == metatype ])
        metatype_group["(metatype = {}) varnodes matched @ MATCH".format(MetaType.repr(metatype))] = matched
        if truth > 0:
            metatype_group["(metatype = {}) varnodes match %".format(MetaType.repr(metatype))] = 100.0 * (matched / truth)
        METRICS["METATYPE SUMMARY ({})".format(MetaType.repr(metatype))] = metatype_group

    array_group = {}
    array_cmps = array_comparisons(cmp)
    array_group["array comparisons"] = len(array_cmps)
    array_group["arrays missed"] = len([ record for record in varnode_compare_records_match_levels(cmp, [VarnodeCompareLevel.NO_MATCH]) if record.get_varnode().get_datatype().get_metatype() == MetaType.ARRAY ])
    if array_cmps:
        array_group["array - avg elements error"] = mean([ array_elements_error(array_cmp) for array_cmp in array_cmps ])
        array_group["array - avg elements error %"] = 100 * mean([ array_elements_error_ratio(array_cmp) for array_cmp in array_cmps ])
        array_group["array - avg size error (bytes)"] = mean([ array_size_error(array_cmp) for array_cmp in array_cmps ])
        array_group["array - avg size error (bytes) %"] = 100 * mean([ array_size_error_ratio(array_cmp) for array_cmp in array_cmps ])
        array_group["array - subtype match %"] = 100 * _array_subtype_match_ratio(array_cmps)
        array_group["array - # of dimensions match %"] = 100 * _array_dimension_match_ratio(array_cmps)

    METRICS["ARRAY RECOVERY"] = array_group

    return METRICS


# def display_metrics(cmp: UnoptimizedProgramInfoCompare2):
#     _map = _mk_metrics(cmp)

#     for grp, metric in _map.items():
#         print("{} {} {}".format("-"*10, grp, "-"*10))
#         for lbl, val in metric.items():
#             print("{} : {}".format(lbl, val))
#         print(),

def display_metrics(cmp: UnoptimizedProgramInfoCompare2):
    metrics_groups = make_metrics()

    for group in metrics_groups:
        print("{} {} {}".format("-"*10, group.get_name(), "-"*10))
        results = group.compute_results(cmp)
        # print(len(group.get_metrics()))
        for result in results:
            print("{} : {}".format(
                result.get_metric().get_display_name(),
                result.get_result()
            ))
        print(),

        