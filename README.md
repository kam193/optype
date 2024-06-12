<h1 align="center">optype</h1>

<p align="center">
    <i>One protocol, one method.</i>
</p>

<p align="center">
    Building blocks for precise & flexible type hints.
</p>

<p align="center">
    <a href="https://github.com/jorenham/optype/actions?query=workflow%3ACI">
        <img
            alt="optype - CI"
            src="https://github.com/jorenham/optype/workflows/CI/badge.svg"
        />
    </a>
    <a href="https://pypi.org/project/optype/">
        <img
            alt="optype - PyPI"
            src="https://img.shields.io/pypi/v/optype?style=flat"
        />
    </a>
    <a href="https://github.com/jorenham/optype">
        <img
            alt="optype - Python Versions"
            src="https://img.shields.io/pypi/pyversions/optype?style=flat"
        />
    </a>
    <a href="https://github.com/jorenham/optype">
        <img
            alt="optype - license"
            src="https://img.shields.io/github/license/jorenham/optype?style=flat"
        />
    </a>
    <a href="https://detachhead.github.io/basedpyright">
        <img
            alt="optype - basedpyright"
            src="https://img.shields.io/badge/basedpyright-checked-42b983"
        />
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img
            alt="optype - ruff"
            src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"
        />
    </a>
</p>

---

## Installation

Optype is available as [`optype`][OPTYPE] on PyPI:

```shell
pip install optype
```

[OPTYPE]: https://pypi.org/project/optype/

## Example

Let's say you're writing a `twice(x)` function, that evaluates `2 * x`.
Implementing it is trivial, but what about the type annotations?

Because `twice(2) == 4`, `twice(3.14) == 6.28` and `twice('I') = 'II'`, it
might seem like a good idea to type it as `twice[T](x: T) -> T: ...`.
However, that wouldn't include cases such as `twice(True) == 2` or
`twice((42, True)) == (42, True, 42, True)`, where the input- and output types
differ.
Moreover, `twice` should accept *any* type with a custom `__rmul__` method
that accepts `2` as argument.

This is where `optype` comes in handy, which has single-method protocols for
*all* the builtin special methods.
For `twice`, we can use `optype.CanRMul[T, R]`, which, as the name suggests,
is a protocol with (only) the `def __rmul__(self, lhs: T) -> R: ...` method.
With this, the `twice` function can written as:

<table>
<tr>
<th width="415px">Python 3.10</th>
<th width="415px">Python 3.12+</th>
</tr>
<tr>
<td>

```python
from typing import Literal
from typing import TypeAlias, TypeVar
from optype import CanRMul

R = TypeVar('R')
Two: TypeAlias = Literal[2]
RMul2: TypeAlias = CanRMul[Two, R]

def twice(x: RMul2[R]) -> R:
    return 2 * x
```

</td>
<td>

```python
from typing import Literal
from optype import CanRMul

type Two = Literal[2]
type RMul2[R] = CanRMul[Two, R]

def twice[R](x: RMul2[R]) -> R:
    return 2 * x
```

</td>
</tr>
</table>

But what about types that implement `__add__` but not `__radd__`?
In this case, we could return `x * 2` as fallback (assuming commutativity).
Because the `optype.Can*` protocols are runtime-checkable, the revised
`twice2` function can be compactly written as:

<table>
<tr>
<th width="415px">Python 3.10</th>
<th width="415px">Python 3.12+</th>
</tr>
<tr>
<td>

```python
from optype import CanMul

Mul2: TypeAlias = CanMul[Two, R]
CMul2: TypeAlias = Mul2[R] | RMul2[R]

def twice2(x: CMul2[R]) -> R:
    if isinstance(x, CanRMul):
        return 2 * x
    else:
        return x * 2
```

</td>
<td>

```python
from optype import CanMul

type Mul2[R] = CanMul[Two, R]
type CMul2[R] = Mul2[R] | RMul2[R]

def twice2[R](x: CMul2[R]) -> R:
    if isinstance(x, CanRMul):
        return 2 * x
    else:
        return x * 2
```

</td>
</tr>
</table>

See [`examples/twice.py`](examples/twice.py) for the full example.

## Overview

The API of `optype` is flat; a single `import optype` is all you need.
There are four flavors of things that live within `optype`,

- `optype.Can{}` types describe *what can be done* with it.
  For instance, any `CanAbs[T]` type can be used as argument to the `abs()`
  builtin function with return type `T`. Most `Can{}` implement a single
  special method, whose name directly matched that of the type. `CanAbs`
  implements `__abs__`, `CanAdd` implements `__add__`, etc.
- `optype.Has{}` is the analogue of `Can{}`, but for special *attributes*.
  `HasName` has the `__name__: str` attribute, `HasDict` has a `__dict__`, etc.
- `optype.Does{}` describe the *type of operators*. So `DoesAbs` is the type
  of the `abs({})` builtin function, and `DoesPos` the type of the `+{}` prefix
  operator.
- `optype.do_{}` are the correctly-typed implementations of `Does{}`. For
  each `do_{}` there is a `Does{}`, and vice-versa. So `do_abs: DoesAbs`
  is the typed alias of `abs({})`, and `do_pos: DoesPos` is a typed version of
  `operator.pos`. The `optype.do_` operators are more complete than
  `operators`, has runtime-accessible type annotations, and uses a fully
  predictable naming scheme.

## Reference

All [typing protocols][PC] here live in the root `optype` namespace.
They are [runtime-checkable][RC] so that you can do e.g.
`isinstance('snail', optype.CanAdd)`, in case you want to check whether
`snail` implements `__add__`.

> [!NOTE]
> It is bad practice to use a [`typing.Protocol`][PC] as base class for your
> implementation. Because of [`@typing.runtime_checkable`][RC], you can use
> `isinstance` either way.

Unlike`collections.abc`, `optype`'s protocols aren't abstract base classes,
i.e. they don't extend `abc.ABC`, only `typing.Protocol`.
This allows the `optype` protocols to be used as building blocks for `.pyi`
type stubs.

[PC]: https://typing.readthedocs.io/en/latest/spec/protocol.html
[RC]: https://typing.readthedocs.io/en/latest/spec/protocol.html#runtime-checkable-decorator-and-narrowing-types-by-isinstance

### Type conversion

The return type of these special methods is *invariant*. Python will raise an
error if some other (sub)type is returned.
This is why these `optype` interfaces don't accept generic type arguments.

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>complex(_)</code></td>
        <td><code>do_complex</code></td>
        <td><code>DoesComplex</code></td>
        <td><code>__complex__</code></td>
        <td><code>CanComplex</code></td>
    </tr>
    <tr>
        <td><code>float(_)</code></td>
        <td><code>do_float</code></td>
        <td><code>DoesFloat</code></td>
        <td><code>__float__</code></td>
        <td><code>CanFloat</code></td>
    </tr>
    <tr>
        <td><code>int(_)</code></td>
        <td><code>do_int</code></td>
        <td><code>DoesInt</code></td>
        <td><code>__int__</code></td>
        <td><code>CanInt[R: int = int]</code></td>
    </tr>
    <tr>
        <td><code>bool(_)</code></td>
        <td><code>do_bool</code></td>
        <td><code>DoesBool</code></td>
        <td><code>__bool__</code></td>
        <td><code>CanBool[R: bool = bool]</code></td>
    </tr>
    <tr>
        <td><code>str(_)</code></td>
        <td><code>do_str</code></td>
        <td><code>DoesStr</code></td>
        <td><code>__str__</code></td>
        <td><code>CanStr[R: str = str]</code></td>
    </tr>
    <tr>
        <td><code>bytes(_)</code></td>
        <td><code>do_bytes</code></td>
        <td><code>DoesBytes</code></td>
        <td><code>__bytes__</code></td>
        <td><code>CanBytes[R: bytes = bytes]</code></td>
    </tr>
</table>

> [!NOTE]
> The types that can be used within `typing.Literal` accept an optional
> type parameter `R`. This can be used to indicate a literal return type,
> for surgically precise typing, e.g. `None`, `True`, and `42` are
> instances of `CanBool[Literal[False]]`, `CanInt[Literal[1]]`, and
> `CanStr[Literal['42']]`, respectively.

These formatting methods are allowed to return instances that are a subtype
of the `str` builtin. The same holds for the `__format__` argument.
So if you're a 10x developer that wants to hack Python's f-strings, but only
if your type hints are spot-on; `optype` is you friend.

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>repr(_)</code></td>
        <td><code>do_repr</code></td>
        <td><code>DoesRepr</code></td>
        <td><code>__repr__</code></td>
        <td><code>CanRepr[R: str = str]</code></td>
    </tr>
    <tr>
        <td><code>format(_, x)</code></td>
        <td><code>do_format</code></td>
        <td><code>DoesFormat</code></td>
        <td><code>__format__</code></td>
        <td><code>CanFormat[T: str = str, R: str = str]</code></td>
    </tr>
</table>

### "Rich comparison" operators

These special methods generally a `bool`. However, instances of any type can
be returned.

<table>
    <tr>
        <th colspan="4" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <td>reflected</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>_ == x</code></td>
        <td><code>x == _</code></td>
        <td><code>do_eq</code></td>
        <td><code>DoesEq</code></td>
        <td><code>__eq__</code></td>
        <td><code>CanEq[T = object, R = bool]</code></td>
    </tr>
    <tr>
        <td><code>_ != x</code></td>
        <td><code>x != _</code></td>
        <td><code>do_ne</code></td>
        <td><code>DoesNe</code></td>
        <td><code>__ne__</code></td>
        <td><code>CanNe[T = object, R = bool]</code></td>
    </tr>
    <tr>
        <td><code>_ < x</code></td>
        <td><code>x > _</code></td>
        <td><code>do_lt</code></td>
        <td><code>DoesLt</code></td>
        <td><code>__lt__</code></td>
        <td><code>CanLt[T, R = bool]</code></td>
    </tr>
    <tr>
        <td><code>_ <= x</code></td>
        <td><code>x >= _</code></td>
        <td><code>do_le</code></td>
        <td><code>DoesLe</code></td>
        <td><code>__le__</code></td>
        <td><code>CanLe[T, R = bool]</code></td>
    </tr>
    <tr>
        <td><code>_ > x</code></td>
        <td><code>x < _</code></td>
        <td><code>do_gt</code></td>
        <td><code>DoesGt</code></td>
        <td><code>__gt__</code></td>
        <td><code>CanGt[T, R = bool]</code></td>
    </tr>
    <tr>
        <td><code>_ >= x</code></td>
        <td><code>x <= _</code></td>
        <td><code>do_ge</code></td>
        <td><code>DoesGe</code></td>
        <td><code>__ge__</code></td>
        <td><code>CanGe[T, R = bool]</code></td>
    </tr>
</table>

### Callable objects

Unlike `operator`, `optype` provides the operator for callable objects:
`optype.do_call(f, *args. **kwargs)`.

`CanCall` is similar to `collections.abc.Callable`, but is runtime-checkable,
and doesn't use esoteric hacks.

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>_(*args, **kwargs)</code></td>
        <td><code>do_call</code></td>
        <td><code>DoesCall</code></td>
        <td><code>__call__</code></td>
        <td><code>CanCall[**Pss, R]</code></td>
    </tr>
</table>

### Numeric operations

For describing things that act like numbers. See the [Python docs][NT] for more
info.

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>_ + x</code></td>
        <td><code>do_add</code></td>
        <td><code>DoesAdd</code></td>
        <td><code>__add__</code></td>
        <td><code>CanAdd[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ - x</code></td>
        <td><code>do_sub</code></td>
        <td><code>DoesSub</code></td>
        <td><code>__sub__</code></td>
        <td><code>CanSub[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ * x</code></td>
        <td><code>do_mul</code></td>
        <td><code>DoesMul</code></td>
        <td><code>__mul__</code></td>
        <td><code>CanMul[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ @ x</code></td>
        <td><code>do_matmul</code></td>
        <td><code>DoesMatmul</code></td>
        <td><code>__matmul__</code></td>
        <td><code>CanMatmul[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ / x</code></td>
        <td><code>do_truediv</code></td>
        <td><code>DoesTruediv</code></td>
        <td><code>__truediv__</code></td>
        <td><code>CanTruediv[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ // x</code></td>
        <td><code>do_floordiv</code></td>
        <td><code>DoesFloordiv</code></td>
        <td><code>__floordiv__</code></td>
        <td><code>CanFloordiv[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ % x</code></td>
        <td><code>do_mod</code></td>
        <td><code>DoesMod</code></td>
        <td><code>__mod__</code></td>
        <td><code>CanMod[T, R]</code></td>
    </tr>
    <tr>
        <td><code>divmod(_, x)</code></td>
        <td><code>do_divmod</code></td>
        <td><code>DoesDivmod</code></td>
        <td><code>__divmod__</code></td>
        <td><code>CanDivmod[T, R]</code></td>
    </tr>
    <tr>
        <td>
            <code>_ ** x</code><br/>
            <code>pow(_, x)</code>
        </td>
        <td><code>do_pow/2</code></td>
        <td><code>DoesPow</code></td>
        <td><code>__pow__</code></td>
        <td>
            <code>CanPow2[T, R]</code><br/>
            <code>CanPow[T, None, R, Never]</code>
        </td>
    </tr>
    <tr>
        <td><code>pow(_, x, m)</code></td>
        <td><code>do_pow/3</code></td>
        <td><code>DoesPow</code></td>
        <td><code>__pow__</code></td>
        <td>
            <code>CanPow3[T, M, R]</code><br/>
            <code>CanPow[T, M, Never, R]</code>
        </td>
    </tr>
    <tr>
        <td><code>_ << x</code></td>
        <td><code>do_lshift</code></td>
        <td><code>DoesLshift</code></td>
        <td><code>__lshift__</code></td>
        <td><code>CanLshift[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ >> x</code></td>
        <td><code>do_rshift</code></td>
        <td><code>DoesRshift</code></td>
        <td><code>__rshift__</code></td>
        <td><code>CanRshift[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ & x</code></td>
        <td><code>do_and</code></td>
        <td><code>DoesAnd</code></td>
        <td><code>__and__</code></td>
        <td><code>CanAnd[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ ^ x</code></td>
        <td><code>do_xor</code></td>
        <td><code>DoesXor</code></td>
        <td><code>__xor__</code></td>
        <td><code>CanXor[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ | x</code></td>
        <td><code>do_or</code></td>
        <td><code>DoesOr</code></td>
        <td><code>__or__</code></td>
        <td><code>CanOr[T, R]</code></td>
    </tr>
</table>

Note that because `pow()` can take an optional third argument, `optype`
provides separate interfaces for `pow()` with two and three arguments.
Additionally, there is the overloaded intersection type
`CanPow[T, M, R, RM] =: CanPow2[T, R] & CanPow3[T, M, RM]`, as interface
for types that can take an optional third argument.

For the binary infix operators above, `optype` additionally provides
interfaces with reflected (swapped) operands:

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>x + _</code></td>
        <td><code>do_radd</code></td>
        <td><code>DoesRAdd</code></td>
        <td><code>__radd__</code></td>
        <td><code>CanRAdd[T, R]</code></td>
    </tr>
    <tr>
        <td><code>x - _</code></td>
        <td><code>do_rsub</code></td>
        <td><code>DoesRSub</code></td>
        <td><code>__rsub__</code></td>
        <td><code>CanRSub[T, R]</code></td>
    </tr>
    <tr>
        <td><code>x * _</code></td>
        <td><code>do_rmul</code></td>
        <td><code>DoesRMul</code></td>
        <td><code>__rmul__</code></td>
        <td><code>CanRMul[T, R]</code></td>
    </tr>
    <tr>
        <td><code>x @ _</code></td>
        <td><code>do_rmatmul</code></td>
        <td><code>DoesRMatmul</code></td>
        <td><code>__rmatmul__</code></td>
        <td><code>CanRMatmul[T, R]</code></td>
    </tr>
    <tr>
        <td><code>x / _</code></td>
        <td><code>do_rtruediv</code></td>
        <td><code>DoesRTruediv</code></td>
        <td><code>__rtruediv__</code></td>
        <td><code>CanRTruediv[T, R]</code></td>
    </tr>
    <tr>
        <td><code>x // _</code></td>
        <td><code>do_rfloordiv</code></td>
        <td><code>DoesRFloordiv</code></td>
        <td><code>__rfloordiv__</code></td>
        <td><code>CanRFloordiv[T, R]</code></td>
    </tr>
    <tr>
        <td><code>x % _</code></td>
        <td><code>do_rmod</code></td>
        <td><code>DoesRMod</code></td>
        <td><code>__rmod__</code></td>
        <td><code>CanRMod[T, R]</code></td>
    </tr>
    <tr>
        <td><code>divmod(x, _)</code></td>
        <td><code>do_rdivmod</code></td>
        <td><code>DoesRDivmod</code></td>
        <td><code>__rdivmod__</code></td>
        <td><code>CanRDivmod[T, R]</code></td>
    </tr>
    <tr>
        <td>
            <code>x ** _</code><br/>
            <code>pow(x, _)</code>
        </td>
        <td><code>do_rpow</code></td>
        <td><code>DoesRPow</code></td>
        <td><code>__rpow__</code></td>
        <td><code>CanRPow[T, R]</code></td>
    </tr>
    <tr>
        <td><code>x << _</code></td>
        <td><code>do_rlshift</code></td>
        <td><code>DoesRLshift</code></td>
        <td><code>__rlshift__</code></td>
        <td><code>CanRLshift[T, R]</code></td>
    </tr>
    <tr>
        <td><code>x >> _</code></td>
        <td><code>do_rrshift</code></td>
        <td><code>DoesRRshift</code></td>
        <td><code>__rrshift__</code></td>
        <td><code>CanRRshift[T, R]</code></td>
    </tr>
    <tr>
        <td><code>x & _</code></td>
        <td><code>do_rand</code></td>
        <td><code>DoesRAnd</code></td>
        <td><code>__rand__</code></td>
        <td><code>CanRAnd[T, R]</code></td>
    </tr>
    <tr>
        <td><code>x ^ _</code></td>
        <td><code>do_rxor</code></td>
        <td><code>DoesRXor</code></td>
        <td><code>__rxor__</code></td>
        <td><code>CanRXor[T, R]</code></td>
    </tr>
    <tr>
        <td><code>x | _</code></td>
        <td><code>do_ror</code></td>
        <td><code>DoesROr</code></td>
        <td><code>__ror__</code></td>
        <td><code>CanROr[T, R]</code></td>
    </tr>
</table>

Note that `CanRPow` corresponds to `CanPow2`; the 3-parameter "modulo" `pow`
does not reflect in Python.

Similarly, the augmented assignment operators are described by the following
`optype` interfaces:

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>_ += x</code></td>
        <td><code>do_iadd</code></td>
        <td><code>DoesIAdd</code></td>
        <td><code>__iadd__</code></td>
        <td><code>CanIAdd[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ -= x</code></td>
        <td><code>do_isub</code></td>
        <td><code>DoesISub</code></td>
        <td><code>__isub__</code></td>
        <td><code>CanISub[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ *= x</code></td>
        <td><code>do_imul</code></td>
        <td><code>DoesIMul</code></td>
        <td><code>__imul__</code></td>
        <td><code>CanIMul[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ @= x</code></td>
        <td><code>do_imatmul</code></td>
        <td><code>DoesIMatmul</code></td>
        <td><code>__imatmul__</code></td>
        <td><code>CanIMatmul[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ /= x</code></td>
        <td><code>do_itruediv</code></td>
        <td><code>DoesITruediv</code></td>
        <td><code>__itruediv__</code></td>
        <td><code>CanITruediv[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ //= x</code></td>
        <td><code>do_ifloordiv</code></td>
        <td><code>DoesIFloordiv</code></td>
        <td><code>__ifloordiv__</code></td>
        <td><code>CanIFloordiv[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ %= x</code></td>
        <td><code>do_imod</code></td>
        <td><code>DoesIMod</code></td>
        <td><code>__imod__</code></td>
        <td><code>CanIMod[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ **= x</code></td>
        <td><code>do_ipow</code></td>
        <td><code>DoesIPow</code></td>
        <td><code>__ipow__</code></td>
        <td><code>CanIPow[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ <<= x</code></td>
        <td><code>do_ilshift</code></td>
        <td><code>DoesILshift</code></td>
        <td><code>__ilshift__</code></td>
        <td><code>CanILshift[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ >>= x</code></td>
        <td><code>do_irshift</code></td>
        <td><code>DoesIRshift</code></td>
        <td><code>__irshift__</code></td>
        <td><code>CanIRshift[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ &= x</code></td>
        <td><code>do_iand</code></td>
        <td><code>DoesIAnd</code></td>
        <td><code>__iand__</code></td>
        <td><code>CanIAnd[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ ^= x</code></td>
        <td><code>do_ixor</code></td>
        <td><code>DoesIXor</code></td>
        <td><code>__ixor__</code></td>
        <td><code>CanIXor[T, R]</code></td>
    </tr>
    <tr>
        <td><code>_ |= x</code></td>
        <td><code>do_ior</code></td>
        <td><code>DoesIOr</code></td>
        <td><code>__ior__</code></td>
        <td><code>CanIOr[T, R]</code></td>
    </tr>
</table>

Additionally, there are the unary arithmetic operators:

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>+_</code></td>
        <td><code>do_pos</code></td>
        <td><code>DoesPos</code></td>
        <td><code>__pos__</code></td>
        <td><code>CanPos[R]</code></td>
    </tr>
    <tr>
        <td><code>-_</code></td>
        <td><code>do_neg</code></td>
        <td><code>DoesNeg</code></td>
        <td><code>__neg__</code></td>
        <td><code>CanNeg[R]</code></td>
    </tr>
    <tr>
        <td><code>~_</code></td>
        <td><code>do_invert</code></td>
        <td><code>DoesInvert</code></td>
        <td><code>__invert__</code></td>
        <td><code>CanInvert[R]</code></td>
    </tr>
    <tr>
        <td><code>abs(_)</code></td>
        <td><code>do_abs</code></td>
        <td><code>DoesAbs</code></td>
        <td><code>__abs__</code></td>
        <td><code>CanAbs[R]</code></td>
    </tr>
</table>

The `round()` built-in function takes an optional second argument.
From a typing perspective, `round()` has two overloads, one with 1 parameter,
and one with two.
For both overloads, `optype` provides separate operand interfaces:
`CanRound1[R]` and `CanRound2[T, RT]`.
Additionally, `optype` also provides their (overloaded) intersection type:
`CanRound[T, R, RT] = CanRound1[R] & CanRound2[T, RT]`.

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>round(_)</code></td>
        <td><code>do_round/1</code></td>
        <td><code>DoesRound</code></td>
        <td><code>__round__/1</code></td>
        <td><code>CanRound1[T = int]</code><br/></td>
    </tr>
    <tr>
        <td><code>round(_, n)</code></td>
        <td><code>do_round/2</code></td>
        <td><code>DoesRound</code></td>
        <td><code>__round__/2</code></td>
        <td><code>CanRound2[T = int, RT = float]</code><br/></td>
    </tr>
    <tr>
        <td><code>round(_, n=...)</code></td>
        <td><code>do_round</code></td>
        <td><code>DoesRound</code></td>
        <td><code>__round__</code></td>
        <td><code>CanRound[T = int, R = int, RT = float]</code></td>
    </tr>
</table>

For example, type-checkers will mark the following code as valid (tested with
pyright in strict mode):

```python
x: float = 3.14
x1: CanRound1[int] = x
x2: CanRound2[int, float] = x
x3: CanRound[int, int, float] = x
```

Furthermore, there are the alternative rounding functions from the
[`math`][MATH] standard library:

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>math.trunc(_)</code></td>
        <td><code>do_trunc</code></td>
        <td><code>DoesTrunc</code></td>
        <td><code>__trunc__</code></td>
        <td><code>CanTrunc[R = int]</code></td>
    </tr>
    <tr>
        <td><code>math.floor(_)</code></td>
        <td><code>do_floor</code></td>
        <td><code>DoesFloor</code></td>
        <td><code>__floor__</code></td>
        <td><code>CanFloor[R = int]</code></td>
    </tr>
    <tr>
        <td><code>math.ceil(_)</code></td>
        <td><code>do_ceil</code></td>
        <td><code>DoesCeil</code></td>
        <td><code>__ceil__</code></td>
        <td><code>CanCeil[R = int]</code></td>
    </tr>
</table>

Almost all implementations use `int` for `R`.
In fact, if no type for `R` is specified, it will default in `int`.
But technially speaking, these methods can be made to return anything.

[MATH]: https://docs.python.org/3/library/math.html
[NT]: https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types

### Async objects

The `optype` variant of `collections.abc.Awaitable[R]`. The only difference
is that `optype.CanAwait[R]` is a pure interface, whereas `Awaitable` is
also an abstract base class.

<table>
    <tr>
        <th align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>await _</code></td>
        <td><code>__await__</code></td>
        <td><code>CanAwait[R]</code></td>
    </tr>
</table>

### Iteration

The operand `x` of `iter(_)` is within Python known as an *iterable*, which is
what `collections.abc.Iterable[V]` is often used for (e.g. as base class, or
for instance checking).

The `optype` analogue is `CanIter[R]`, which as the name suggests,
also implements `__iter__`. But unlike `Iterable[V]`, its type parameter `R`
binds to the return type of `iter(_) -> R`. This makes it possible to annotate
the specific type of the *iterable* that `iter(_)` returns. `Iterable[V]` is
only able to annotate the type of the iterated value. To see why that isn't
possible, see [python/typing#548](https://github.com/python/typing/issues/548).

The `collections.abc.Iterator[V]` is even more awkward; it is a subtype of
`Iterable[V]`. For those familiar with `collections.abc` this might come as a
surprise, but an iterator only needs to implement `__next__`, `__iter__` isn't
needed. This means that the `Iterator[V]` is unnecessarily restrictive.
Apart from that being theoretically "ugly", it has significant performance
implications, because the time-complexity of `isinstance` on a
`typing.Protocol` is $O(n)$, with the $n$ referring to the amount of members.
So even if the overhead of the inheritance and the `abc.ABC` usage is ignored,
`collections.abc.Iterator` is twice as slow as it needs to be.

That's one of the (many) reasons that `optype.CanNext[V]` and
`optype.CanNext[V]` are the better alternatives to `Iterable` and `Iterator`
from the abracadabra collections. This is how they are defined:

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>next(_)</code></td>
        <td><code>do_next/1</code></td>
        <td><code>DoesNext</code></td>
        <td><code>__next__</code></td>
        <td><code>CanNext[V]</code></td>
    </tr>
    <tr>
        <td><code>iter(_)</code></td>
        <td><code>do_iter/1</code></td>
        <td><code>DoesIter</code></td>
        <td><code>__iter__</code></td>
        <td><code>CanIter[R: CanNext[Any]]</code></td>
    </tr>
</table>

For the sake of compatibility with `collections.abc`, there is
`optype.CanIterSelf[V]`, which is a protocol whose `__iter__` returns
`typing.Self`, as well as a `__next__` method that returns `T`.
I.e. it is equivalent to `collections.abc.Iterator[V]`, but without the `abc`
nonsense.

### Async Iteration

Yes, you guessed it right; the abracadabra collections made the exact same
mistakes for the async iterablors (or was it "iteramblers"...?).

But fret not; the `optype` alternatives are right here:

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>anext(_)</code></td>
        <td><code>do_anext</code></td>
        <td><code>DoesANext</code></td>
        <td><code>__anext__</code></td>
        <td><code>CanANext[V]</code></td>
    </tr>
    <tr>
        <td><code>aiter(_)</code></td>
        <td><code>do_aiter</code></td>
        <td><code>DoesAIter</code></td>
        <td><code>__aiter__</code></td>
        <td><code>CanAIter[R: CanAnext[Any]]</code></td>
    </tr>
</table>

But wait, shouldn't `V` be a `CanAwait`? Well, only if you don't want to get
fired...
Technically speaking, `__anext__` can return any type, and `anext` will pass
it along without nagging (instance checks are slow, now stop bothering that
liberal). For details, see the discussion at [python/typeshed#7491][AN].
Just because something is legal, doesn't mean it's a good idea (don't eat the
yellow snow).

Additionally, there is `optype.CanAIterSelf[R]`, with both the
`__aiter__() -> Self` and the `__anext__() -> V` methods.

[AN]: https://github.com/python/typeshed/pull/7491

### Containers

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>len(_)</code></td>
        <td><code>do_len</code></td>
        <td><code>DoesLen</code></td>
        <td><code>__len__</code></td>
        <td><code>CanLen[R: int = int]</code></td>
    </tr>
    <tr>
        <td>
            <code>_.__length_hint__()</code>
            (<a href="https://docs.python.org/3/reference/datamodel.html#object.__length_hint__">docs</a>)
        </td>
        <td><code>do_length_hint</code></td>
        <td><code>DoesLengthHint</code></td>
        <td><code>__length_hint__</code></td>
        <td><code>CanLengthHint[R: int = int]</code></td>
    </tr>
    <tr>
        <td><code>_[k]</code></td>
        <td><code>do_getitem</code></td>
        <td><code>DoesGetitem</code></td>
        <td><code>__getitem__</code></td>
        <td><code>CanGetitem[K, V]</code></td>
    </tr>
    <tr>
        <td>
            <code>_.__missing__()</code>
            (<a href="https://docs.python.org/3/reference/datamodel.html#object.__missing__">docs</a>)
        </td>
        <td><code>do_missing</code></td>
        <td><code>DoesMissing</code></td>
        <td><code>__missing__</code></td>
        <td><code>CanMissing[K, D]</code></td>
    </tr>
    <tr>
        <td><code>_[k] = v</code></td>
        <td><code>do_setitem</code></td>
        <td><code>DoesSetitem</code></td>
        <td><code>__setitem__</code></td>
        <td><code>CanSetitem[K, V]</code></td>
    </tr>
    <tr>
        <td><code>del _[k]</code></td>
        <td><code>do_delitem</code></td>
        <td><code>DoesDelitem</code></td>
        <td><code>__delitem__</code></td>
        <td><code>CanDelitem[K]</code></td>
    </tr>
    <tr>
        <td><code>k in _</code></td>
        <td><code>do_contains</code></td>
        <td><code>DoesContains</code></td>
        <td><code>__contains__</code></td>
        <td><code>CanContains[K = object]</code></td>
    </tr>
    <tr>
        <td><code>reversed(_)</code></td>
        <td><code>do_reversed</code></td></td>
        <td><code>DoesReversed</code></td>
        <td><code>__reversed__</code></td>
        <td>
            <code>CanReversed[R]</code>, or<br>
            <code>CanSequence[K: CanIndex, V]</code>
        </td>
    </tr>
</table>

Because `CanMissing[K, D]` generally doesn't show itself without
`CanGetitem[K, V]` there to hold its hand, `optype` conveniently stitched them
together as `optype.CanGetMissing[K, V, D=V]`.

Similarly, there is `optype.CanSequence[K: CanIndex | slice, V]`, which is the
combination of both `CanLen` and `CanItem[I, V]`, and serves as a more
specific and flexible `collections.abc.Sequence[V]`.

Additionally, `optype` provides protocols for types with (custom) *hash* or
*index* methods:

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>hash(_)</code></td>
        <td><code>do_hash</code></td>
        <td><code>DoesHash</code></td>
        <td><code>__hash__</code></td>
        <td><code>CanHash</code></td>
    </tr>
    <tr>
        <td>
            <code>_.__index__()</code>
            (<a href="https://docs.python.org/3/reference/datamodel.html#object.__index__">docs</a>)
        </td>
        <td><code>do_index</code></td>
        <td><code>DoesIndex</code></td>
        <td><code>__index__</code></td>
        <td><code>CanIndex[R: int = int]</code></td>
    </tr>
</table>

### Attribute access

<table>
    <tr>
        <th colspan="3" align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <th>function</th>
        <th>type</th>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td>
            <code>v = _.k</code> or<br/>
            <code>v = getattr(_, k)</code>
        </td>
        <td><code>do_getattr</code></td>
        <td><code>DoesGetattr</code></td>
        <td><code>__getattr__</code></td>
        <td><code>CanGetattr[K: str = str, V = Any]</code></td>
    </tr>
    <tr>
        <td>
            <code>_.k = v</code> or<br/>
            <code>setattr(_, k, v)</code>
        </td>
        <td><code>do_setattr</code></td>
        <td><code>DoesSetattr</code></td>
        <td><code>__setattr__</code></td>
        <td><code>CanSetattr[K: str = str, V = Any]</code></td>
    </tr>
    <tr>
        <td>
            <code>del _.k</code> or<br/>
            <code>delattr(_, k)</code>
        </td>
        <td><code>do_delattr</code></td>
        <td><code>DoesDelattr</code></td>
        <td><code>__delattr__</code></td>
        <td><code>CanDelattr[K: str = str]</code></td>
    </tr>
    <tr>
        <td><code>dir(_)</code></td>
        <td><code>do_dir</code></td>
        <td><code>DoesDir</code></td>
        <td><code>__dir__</code></td>
        <td><code>CanDir[R: CanIter[CanIterSelf[str]]]</code></td>
    </tr>
</table>

### Descriptors

Interfaces for [descriptors](https://docs.python.org/3/howto/descriptor.html).

<table>
    <tr>
        <th align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td>
            <code>v: V = T().d</code><br/>
            <code>vt: VT = T.d</code>
        </td>
        <td><code>__get__</code></td>
        <td><code>CanGet[T: object, V, VT = V]</code></td>
    </tr>
    <tr>
        <td><code>T().k = v</code></td>
        <td><code>__set__</code></td>
        <td><code>CanSet[T: object, V]</code></td>
    </tr>
    <tr>
        <td><code>del T().k</code></td>
        <td><code>__delete__</code></td>
        <td><code>CanDelete[T: object]</code></td>
    </tr>
    <tr>
        <td><code>class T: d = _</code></td>
        <td><code>__set_name__</code></td>
        <td><code>CanSetName[T: object, N: str = str]</code></td>
    </tr>
</table>

### Context managers

Support for the `with` statement.

<table>
    <tr>
        <th align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <td>method(s)</td>
        <th>type</th>
    </tr>
    <tr>
        <td></td>
        <td><code>__enter__</code></td>
        <td><code>CanEnter[C]</code></td>
    </tr>
    <tr>
        <td></td>
        <td><code>__exit__</code></td>
        <td><code>CanExit[R = None]</code></td>
    </tr>
    <tr>
        <td><code>with _ as v</code></td>
        <td><code>__enter__</code>, <code>__exit__</code></td>
        <td><code>CanWith[C, R = None]</code></td>
    </tr>
</table>

For the `async with` statement the interfaces look very similar:

<table>
    <tr>
        <th align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <td>method(s)</td>
        <th>type</th>
    </tr>
    <tr>
        <td></td>
        <td><code>__aenter__</code></td>
        <td><code>CanAEnter[C]</code></td>
    </tr>
    <tr>
        <td></td>
        <td><code>__aexit__</code></td>
        <td><code>CanAExit[R = None]</code></td>
    </tr>
    <tr>
        <td><code>async with _ as v</code></td>
        <td><code>__aenter__</code>, <code>__aexit__</code></td>
        <td><code>CanAsyncWith[C, R = None]</code></td>
    </tr>
</table>

### Buffer types

Interfaces for emulating buffer types using the [buffer protocol][BP].

<table>
    <tr>
        <th align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>v = memoryview(_)</code></td>
        <td><code>__buffer__</code></td>
        <td><code>CanBuffer[T: int = int]</code></td>
    </tr>
    <tr>
        <td><code>del v</code></td>
        <td><code>__release_buffer__</code></td>
        <td><code>CanReleaseBuffer</code></td>
    </tr>
</table>

[BP]: https://docs.python.org/3/reference/datamodel.html#python-buffer-protocol

### `copy`

For the [`copy`][CP] standard library, `optype` provides the following
interfaces:

<table>
    <tr>
        <th align="center">operator</th>
        <th colspan="2" align="center">operand</th>
    </tr>
    <tr>
        <td>expression</td>
        <td>method</td>
        <th>type</th>
    </tr>
    <tr>
        <td><code>copy.copy(_)</code></td>
        <td><code>__copy__</code></td>
        <td><code>CanCopy[R: object]</code></td>
    </tr>
    <tr>
        <td><code>copy.deepcopy(_, memo={})</code></td>
        <td><code>__deepcopy__</code></td>
        <td><code>CanDeepcopy[R: object]</code></td>
    </tr>
    <tr>
        <td><code>copy.replace(_, **changes: V)</code> (Python 3.13+)</td>
        <td><code>__replace__</code></td>
        <td><code>CanReplace[V, R]</code></td>
    </tr>
</table>

And for convenience, there are the runtime-checkable aliases for all three
interfaces, with `R` bound to `Self`.
These are roughly equivalent to:

```python
type CanCopySelf = CanCopy[CanCopySelf]
type CanDeepcopySelf = CanDeepcopy[CanDeepcopySelf]
type CanReplaceSelf[V] = CanReplace[V, CanReplaceSelf[V]]
```

[CP]: https://docs.python.org/3/library/copy.html

### `pickle`

For the [`pickle`][PK] standard library, `optype` provides the following
interfaces:

[PK]: https://docs.python.org/3/library/pickle.html

<table>
    <tr>
        <th>method(s)</th>
        <th>signature (bound)</th>
        <th>type</th>
    </tr>
    <tr>
        <td><code>__reduce__</code></td>
        <td><code>() -> R</code></td>
        <td><code>CanReduce[R: str | tuple = str | tuple]</code></td>
    </tr>
    <tr>
        <td><code>__reduce_ex__</code></td>
        <td><code>(CanIndex) -> R</code></td>
        <td><code>CanReduceEx[R: str | tuple = str | tuple]</code></td>
    </tr>
    <tr>
        <td><code>__getstate__</code></td>
        <td><code>() -> S</code></td>
        <td><code>CanGetstate[S: object]</code></td>
    </tr>
    <tr>
        <td><code>__setstate__</code></td>
        <td><code>(S) -> None</code></td>
        <td><code>CanSetstate[S: object]</code></td>
    </tr>
    <tr>
        <td>
            <code>__getnewargs__</code><br>
            <code>__new__</code>
        </td>
        <td>
            <code>() -> tuple[*Vs]</code><br>
            <code>(*Vs) -> Self</code><br>
        </td>
        <td><code>CanGetnewargs[*Vs]</code></td>
    </tr>
    <tr>
        <td>
            <code>__getnewargs_ex__</code><br>
            <code>__new__</code>
        </td>
        <td>
            <code>() -> tuple[tuple[*Vs], dict[str, V]]</code><br>
            <code>(*Vs, **dict[str, V]) -> Self</code><br>
        </td>
        <td><code>CanGetnewargsEx[*Vs, V]</code></td>
    </tr>
</table>

### `dataclasses`

For the [`dataclasses`][DC] standard library, `optype` provides the
`HasDataclassFields[V: Mapping[str, Field]]` interface.
It can conveniently be used to check whether a type or instance is a
dataclass, i.e. `isinstance(obj, optype.HasDataclassFields)`.

[DC]: https://docs.python.org/3/library/dataclasses.html

## Future plans

- [numpy][NP] interfaces for arrays-like types (no deps) (#24)
- [array-api][API-ND] interfaces (no deps) (#25)
- [dataframe-api][API-DF] interfaces (no deps) (#26)

[NP]: https://github.com/numpy/numpy
[API-ND]: https://data-apis.org/array-api/latest/
[API-DF]: https://data-apis.org/dataframe-api/draft/index.html
