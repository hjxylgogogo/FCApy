import pytest
from fcapy.context import FormalContext, read_cxt, read_json, read_csv
from .data_to_test import animal_movement_data
from operator import itemgetter


def test_data_property(animal_movement_data):
    ctx = FormalContext()

    data = animal_movement_data['data']
    ctx = FormalContext(data=data)
    data_ = ctx.data
    assert data == data_, 'FormalContext.data has changed the initial data'

    with pytest.raises(AssertionError):
        FormalContext(data=[])

    with pytest.raises(AssertionError):
        FormalContext(data=[[0], [1, 2]])


def test_object_attribute_names(animal_movement_data):
    data, obj_names, attr_names = itemgetter('data', 'obj_names', 'attr_names')(animal_movement_data)

    ctx = FormalContext(data=data)
    obj_names_default = [str(idx) for idx in range(len(obj_names))]
    assert ctx.object_names == obj_names_default,\
        f'FormalContext.object_names failed. Default object names should be {obj_names_default}'
    attr_names_default = [str(idx) for idx in range(len(attr_names))]
    assert ctx.attribute_names == attr_names_default, \
        f'FormalContext.attribute_names failed. Default attribute names should be {attr_names_default}'

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    assert ctx.object_names == obj_names, 'FormalContext.object_names has changed the initial object_names'
    assert ctx.attribute_names == attr_names, 'FormalContext.attribute_names has changed the initial attribute_names'

    with pytest.raises(AssertionError):
        ctx.attribute_names = []
    with pytest.raises(AssertionError):
        ctx.object_names = [1, 2]


def test_intent_extent_i(animal_movement_data):
    data = animal_movement_data['data']
    ctx = FormalContext(data=data)
    ext_ = ctx.extension_i([0, 1])
    assert set(ext_) == {4, 5, 6}, 'FormalContext.extension_i failed. Should be {4, 5, 6}'

    int_ = ctx.intention_i([4, 5, 6])
    assert set(int_) == {0, 1}, 'FormalContext.intention_i failed. Should be {0, 1}'

    assert ctx.intention_i(ctx.extension_i(int_)) == int_,\
        'Basic FCA theorem failed. Check FormalContext.extension_i, intention_i'


def test_intent_extent(animal_movement_data):
    data, obj_names, attr_names = itemgetter('data', 'obj_names', 'attr_names')(animal_movement_data)

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    ext_ = ctx.extension(['fly', 'hunt'])
    assert set(ext_) == {'owl', 'hawk', 'eagle'}, 'FormalContext.extension failed. Should be {"owl", "hawk", "eagle"}'

    int_ = ctx.intention(['owl', 'hawk', 'eagle'])
    assert set(int_) == {'fly', 'hunt'}, 'FormalContext.intention failed. Should be {"fly","hunt"}'

    assert ctx.intention(ctx.extension(int_)) == int_,\
        'Basic FCA theorem failed. Check FormalContext.extension, intention'

    with pytest.raises(KeyError):
        ctx.intention(['d1'])
    with pytest.raises(KeyError):
        ctx.extension((['z93']))


def test_n_objects(animal_movement_data):
    data, obj_names = itemgetter('data', 'obj_names')(animal_movement_data)

    ctx = FormalContext()
    assert ctx.n_objects is None, 'FormalContext.n_objects failed. Should be None since no data in the context'

    ctx = FormalContext(data=data)
    assert ctx.n_objects == len(obj_names), f'FormalContext.n_objects failed. '\
                                            + f'Should be {len(obj_names)} since data has {len(obj_names)} lines'

    with pytest.raises(AttributeError):
        ctx.n_objects = 42


def test_n_attributes(animal_movement_data):
    data, attr_names = itemgetter('data', 'attr_names')(animal_movement_data)
    ctx = FormalContext()
    assert ctx.n_attributes is None, 'FormalContext.n_attributes failed. Should be None since no data in the context'

    ctx = FormalContext(data=data)
    assert ctx.n_attributes == len(attr_names),\
        f'FormalContext.n_attributes failed. '\
        + f'Should be {len(attr_names)} since each line in data is of length {(len(attr_names))}'

    with pytest.raises(AttributeError):
        ctx.n_attributes = 42


def test_description():
    ctx = FormalContext()
    ctx.description = 'Test description'
    assert ctx.description == 'Test description',\
        'FormalContext.description failed. The description differs from the given "Test description"'

    with pytest.raises(AssertionError):
        ctx.description = 42


def test_to_funcs(animal_movement_data):
    path = animal_movement_data['path']
    for fnc_read, file_extension in [(read_cxt, '.cxt'),
                                     (read_json, '.json'),
                                     (read_csv, '.csv')
                                     ]:
        path_ext = path+file_extension

        with open(path_ext, 'r') as f:
            file_orig = f.read()

        ctx = fnc_read(path_ext)
        fnc_write = {'.cxt': ctx.to_cxt,
                     '.json': ctx.to_json,
                     '.csv': ctx.to_csv
                     }[file_extension]
        fnc_name = fnc_write.__name__

        file_new = fnc_write()
        assert file_new == file_orig,\
            f'FormalContext.{fnc_name} failed. Result context file does not math the initial one'


def test_print_data(animal_movement_data):
    data, obj_names, attr_names, printed_data_short = \
        itemgetter('data', 'obj_names', 'attr_names', 'printed_data_short')(animal_movement_data)

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    s = ctx.print_data(max_n_objects=4, max_n_attributes=2)
    assert s == printed_data_short, 'FormalContext.print_data failed. Check data formatting.'


def test_repr(animal_movement_data):
    data, obj_names, attr_names, repr_data = \
        itemgetter('data', 'obj_names', 'attr_names', 'repr_data')(animal_movement_data)

    ctx = FormalContext(data=data, object_names=obj_names, attribute_names=attr_names)
    s = ctx.__repr__()
    assert s == repr_data, "FormalContext.__repr__ failed. '" \
                           + "Check print_data parameters: max_n_objects=20, max_n_attributes=10."
