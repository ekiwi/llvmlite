"""
This file demonstrates how to operate on LLVM IR vectors.
"""

from llvmlite import ir

# use a single lane on haswell
vector_width = 128
sample_t = ir.IntType(8)
sample_count = vector_width // sample_t.width
assert sample_count * sample_t.width == vector_width

vec_t = ir.VectorType(sample_t, sample_count)
shuffle_t = ir.VectorType(ir.IntType(32), sample_count)
fun_t = ir.FunctionType(vec_t, (vec_t, vec_t))

# TODO: add actual tests similar to "test_array"
mask = ir.Constant(vec_t, 0xffff)
print("vec_t", str(vec_t))
print("mask", str(mask))


module = ir.Module(name=__file__)
func = ir.Function(module, fun_t, name="foo")

# Now implement the function
block = func.append_basic_block(name="entry")
builder = ir.IRBuilder(block)
high, last_chunk = func.args
mask = ir.Constant(vec_t, (0xffff,) * sample_count)
zero = ir.Constant(vec_t, (0,) * sample_count)
low = builder.xor(high, mask, name="low")
oldest_id = sample_count - 1
latest_id = 2 * sample_count - 2
shift_one_into_past = ir.Constant(shuffle_t, list(range(oldest_id,latest_id+1)))
prev_high = builder.shuffle_vector(last_chunk, high, shift_one_into_past, name="prev_high")
prev_low = builder.xor(prev_high, mask, name="prev_low")
falling = builder.and_(prev_low, high, name="falling")
rising = builder.and_(prev_high, low, name="rising")
any_falling = builder.not_(builder.icmp_signed('==',falling, zero))
builder.ret(falling)

# Print the module IR
#import pdb; pdb.set_trace()
print(module)
