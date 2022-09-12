"""
This module offers a class BinTable to work with binary table efficiently.

"""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional, Collection, Any, Type

from fcapy import LIB_INSTALLED
if LIB_INSTALLED['bitsets']:
    import bitsets

if LIB_INSTALLED['bitarray']:
    from bitarray import frozenbitarray as fbitarray
    from bitarray import bitarray

if LIB_INSTALLED['numpy']:
    import numpy as np
    import numpy.typing as npt


@dataclass
class UnmatchedTypeError(ValueError):
    row_idx: int

    def __str__(self):
        msg = '\n'.join([
            f'All rows should of the given `data` should be of the same type. '
            f'The problem is with the row #{self.row_idx}'
        ])
        return msg


@dataclass
class UnmatchedLengthError(ValueError):
    row_idx: int = None

    def __str__(self):
        msg = '\n'.join([
            f'All rows should of the given `data` should be of the same length. ',
            f'The problem is with the row #{self.row_idx}' if self.row_idx else ''
        ]).strip()
        return msg


@dataclass
class NotBooleanValueError(ValueError):
    row_idx: int = None

    def __str__(self):
        msg = '\n'.join([
            f"All values in each row should be of type bool.",
            f"The problem is with the row #{self.row_idx}" if self.row_idx else ''
        ]).strip()
        return msg


@dataclass
class UnknownDataTypeError(TypeError):
    unknown_type: type

    def __str__(self):
        msg = '\n'.join([
            "Dont know how to process the given `data`. ",
            "Acceptable types of data: List[List[bool]], npt.NDArray[bool], List[fbitarray]. ",
            f"The given type: {self.unknown_type}"
        ]).strip()
        return msg


@dataclass
class UnknownAxisError(TypeError):
    unknown_axis: Any
    known_axes: set = frozenset({None, 0, 1})

    def __str__(self):
        msg = '\n'.join([
            f"Unknown `axis` value passed: {self.unknown_axis}. ",
            f"Supported values are: {self.known_axes}"
        ]).strip()
        return msg


class AbstractBinTable(metaclass=ABCMeta):
    def __init__(self, data: List[List[bool]] = None):
        self.data = data

    @property
    def data(self) -> Collection:
        return self._data

    @data.setter
    def data(self, value):
        data, h, w = self._transform_data(value)
        self._validate_data(data)
        self._data, self._height, self._width = data, h, w

    @property
    def height(self) -> Optional[int]:
        return self._height

    @property
    def width(self) -> Optional[int]:
        return self._width

    @property
    def shape(self) -> Optional[Tuple[int, Optional[int]]]:
        return self.height, self.width

    def all(self, axis: int = None) -> bool or Collection[bool]:
        if axis not in {None, 0, 1}:
            raise UnknownAxisError(axis)

        if axis is None:
            return self._all()
        if axis == 0:
            return self._all_per_column()
        if axis == 1:
            return self._all_per_row()

    def all_i(self, axis: int) -> Collection[int]:
        return [i for i, flg in enumerate(self.all(axis)) if flg]

    def any(self, axis: int = None) -> bool or Collection[bool]:
        if axis not in {None, 0, 1}:
            raise UnknownAxisError(axis)

        if axis is None:
            return self._any()
        if axis == 0:
            return self._any_per_column()
        if axis == 1:
            return self._any_per_row()

    def any_i(self, axis: int) -> Collection[int]:
        return [i for i, flg in enumerate(self.any(axis)) if flg]

    def sum(self, axis: int = None) -> int or Collection[int]:
        if axis not in {None, 0, 1}:
            raise UnknownAxisError(axis)

        if axis is None:
            return self._sum()
        if axis == 0:
            return self._sum_per_column()
        if axis == 1:
            return self._sum_per_row()

    def to_lists(self) -> List[List[bool]]:
        return [[bool(v) for v in row] for row in self.data]

    def to_tuples(self) -> Tuple[Tuple[bool, ...], ...]:
        return tuple([tuple(row) for row in self.to_lists()])

    def __hash__(self):
        return hash(self.to_tuples())

    def __eq__(self, other: 'AbstractBinTable') -> bool:
        if self.height != other.height:
            return False
        if self.width != other.width:
            return False
        return self.data == other.data

    @abstractmethod
    def _validate_data(self, data) -> bool:
        ...

    def _transform_data(self, data) -> Tuple[Collection, int, Optional[int]]:
        if data is None:
            return [], 0, None

        dclass = self.decide_dataclass(data)
        if dclass == self.__class__.__name__:
            return self._transform_data_inherent(data)

        bt = BINTABLE_CLASSES[dclass](data)
        return self._transform_data_fromlists(bt.to_lists()), bt.height, bt.width

    @staticmethod
    def _transform_data_inherent(data) -> Tuple[Collection, int, int]:
        return data, len(data), len(data[0])

    @abstractmethod
    def _transform_data_fromlists(self, data: List[List[bool]]) -> Collection:
        ...

    @abstractmethod
    def _all(self) -> bool:
        ...

    @abstractmethod
    def _all_per_row(self) -> List[bool]:
        ...

    @abstractmethod
    def _all_per_column(self) -> List[bool]:
        ...

    @abstractmethod
    def _any(self) -> bool:
        ...

    @abstractmethod
    def _any_per_row(self) -> List[bool]:
        ...

    @abstractmethod
    def _any_per_column(self) -> List[bool]:
        ...

    @abstractmethod
    def _sum(self) -> int:
        ...

    @abstractmethod
    def _sum_per_row(self) -> List[int]:
        ...

    @abstractmethod
    def _sum_per_column(self) -> List[int]:
        ...

    def __len__(self):
        return self.height

    def __getitem__(self, item):
        print(item, type(item))
        if isinstance(item, int):
            return self.data[item]

        if isinstance(item, (slice, list)):
            return self.__class__(self.data[item])

        if isinstance(item, tuple):
            row_slicer, column_slicer = item

            row_single_slice, column_single_slice = [isinstance(x, int) for x in [row_slicer, column_slicer]]
            if row_single_slice and column_single_slice:
                return self.data[row_slicer][column_slicer]
            if row_single_slice and not column_single_slice:
                return self._slice_row(self.data[row_slicer], column_slicer)
            if not row_single_slice and column_single_slice:
                return self._slice_column(self.data[row_slicer], column_slicer)
            if not row_single_slice and not column_single_slice:
                return self.__class__(self.data[row_slicer, column_slicer])

        raise NotImplementedError("Unknown `item` to slice the BinTable")

    @staticmethod
    def _slice_row(row: Collection, slicer: int or List[int] or slice) -> Collection:
        return row[slicer]

    @staticmethod
    def _slice_column(data: Collection, slicer: int or List[int] or slice) -> Collection:
        return [row[slicer] for row in data]

    @staticmethod
    def decide_dataclass(data: Collection) -> str:  # Type['AbstractBinTable']:
        assert len(data) > 0, "Too small data to decide what class does it belong to"
        if isinstance(data, list) and isinstance(data[0], list):
            return 'BinTableLists'
        if isinstance(data, list) and isinstance(data[0], fbitarray):
            return 'BinTableBitarray'
        if isinstance(data, np.ndarray):
            return 'BinTableNumpy'

        raise UnknownDataTypeError(type(data))


class BinTableLists(AbstractBinTable):
    data: List[List[bool]]  # Updating type hint

    def to_lists(self) -> List[List[bool]]:
        return self.data

    def _validate_data(self, data: List[List[bool]]) -> bool:
        if len(data) == 0:
            return True

        t_, l_ = type(data[0]), len(data[0])
        for i, row in enumerate(data):
            if type(row) != t_:
                raise UnmatchedTypeError(i)
            if len(row) != l_:
                raise UnmatchedLengthError(i)
            for v in row:
                if not isinstance(v, bool):
                    raise NotBooleanValueError(i)

        return True

    def _transform_data_fromlists(self, data: List[List[bool]]) -> List[List[bool]]:
        return data

    def _all(self) -> bool:
        for row in self.data:
            if not all(row):
                return False
        return True

    def _all_per_row(self) -> List[bool]:
        return [all(row) for row in self.data]

    def _all_per_column(self) -> List[bool]:
        return [all(col) for col in zip(*self.data)]

    def _any(self) -> bool:
        for row in self.data:
            if any(row):
                return True
        return False

    def _any_per_row(self) -> List[bool]:
        return [any(row) for row in self.data]

    def _any_per_column(self) -> List[bool]:
        return [any(col) for col in zip(*self.data)]

    def _sum(self) -> int:
        return sum(self._sum_per_row())

    def _sum_per_row(self) -> List[int]:
        return [sum(row) for row in self.data]

    def _sum_per_column(self) -> List[int]:
        return [sum(col) for col in zip(*self.data)]


class BinTableNumpy(AbstractBinTable):
    data: npt.NDArray[bool]  # Updating type hint

    def _transform_data_fromlists(self, data: List[List[bool]]) -> npt.NDArray[bool]:
        return np.array(data)

    def _validate_data(self, data: npt.NDArray[bool]) -> bool:
        if len(data) == 0:
            return True

        if data.dtype != 'bool':
            raise NotBooleanValueError()

        if len(data.shape) != 2:
            raise UnmatchedLengthError()

        return True

    def _all(self) -> bool:
        return self.data.all()

    def _all_per_row(self) -> npt.NDArray[bool]:
        return self.data.all(1)

    def _all_per_column(self) -> npt.NDArray[bool]:
        return self.data.all(0)

    def _any(self) -> bool:
        return self.data.any()

    def _any_per_row(self) -> npt.NDArray[bool]:
        return self.data.any(1)

    def _any_per_column(self) -> npt.NDArray[bool]:
        return self.data.any(0)

    def _sum(self) -> int:
        return self.data.sum()

    def _sum_per_row(self) -> npt.NDArray[int]:
        return self.data.sum(1)

    def _sum_per_column(self) -> npt.NDArray[int]:
        return self.data.sum(0)

    def __eq__(self, other: 'BinTableNumpy'):
        if self.height != other.height:
            return False
        if self.width != other.width:
            return False
        return (self.data == other.data).all()

    def __hash__(self):
        return hash(self.to_tuples())


class BinTableBitarray(AbstractBinTable):
    data: List[fbitarray]  # Updating type hint

    def _transform_data_fromlists(self, data: List[List[bool]]) -> List[fbitarray]:
        return [fbitarray(row) for row in data]

    def _validate_data(self, data: List[fbitarray]) -> bool:
        if len(data) == 0:
            return True

        l_ = len(data[0])
        for i, row in enumerate(data):
            if len(row) != l_:
                raise UnmatchedLengthError(i)

        return True

    def _all(self) -> bool:
        for row in self.data:
            if not row.all():
                return False
        return True

    def _all_per_row(self) -> fbitarray:
        return fbitarray([row.all() for row in self.data])

    def _all_per_column(self) -> fbitarray:
        vals = bitarray(self.data[0])
        for row in self.data[1:]:
            vals &= row
            if not vals.any():  # If all values are False
                return vals
        return vals

    def _any(self) -> bool:
        for row in self.data:
            if row.any():
                return True
        return False

    def _any_per_row(self) -> fbitarray:
        return fbitarray([row.any() for row in self.data])

    def _any_per_column(self) -> fbitarray:
        vals = bitarray(self.data[0])
        for row in self.data[1:]:
            vals |= row
            if vals.all():
                return vals
        return vals

    def _sum(self) -> int:
        return sum(self._sum_per_row())

    def _sum_per_row(self) -> List[int]:
        return [row.count() for row in self.data]

    def _sum_per_column(self) -> List[int]:
        vals = [0] * self.width
        for row in self.data:
            for v in row.search(1):
                vals[v] += 1
        return vals

    def __eq__(self, other: 'BinTableBitarray'):
        if self.height != other.height:
            return False
        if self.width != other.width:
            return False
        return self.data == other.data

    def __hash__(self):
        return hash(tuple(self.data))


BINTABLE_CLASSES = {cl.__name__: cl for cl in [BinTableLists, BinTableNumpy, BinTableBitarray]}
