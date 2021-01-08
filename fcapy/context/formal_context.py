class FormalContext:
    """
    A class used to represent Formal Context object from FCA theory.

    Methods
    -------
    intention(objects)
        Return maximal set of attributes which are shared by given ``objects``
    extension(attributes)
        Return maximal set of objects which share given ``attributes``
    intention_i(object_indexes)
        Offer the same logic as intention(...) but objects and attributes are defined by their indexes
    extension_i(attribute_indexes)
        Offer the same logic as extension(...) but objects and attributes are defined by their indexes

    to_cxt(path=None)
        Convert the FormalContext into cxt file format (save if ``path`` is given)
    to_json(path=None)
        Convert the FormalContext into json file format (save if ``path`` is given)
    to_csv(path=None, **kwargs)
        Convert the FormalContext into csv file format (save if ``path`` is given)
    to_pandas()
        Convert the FormalContext into pandas.DataFrame object

    Notes
    -----
    Formal Context K = (G, M, I) - is a triplet of:
    1. set of objects G (the property ``object_names`` in this class)
    2. set of attributes M (the property ``attribute_names`` in this class)
    3. binary relation I between G and M (i.e. "gIm holds True" means "object g has attribute m")
      (the property ``data`` in this class)

    """

    def __init__(self, data=None, object_names=None, attribute_names=None, **kwargs):
        """
        Parameters
        ----------
        data : `list of `list
            Two dimensional list of bool variables.
            "data[i][j] = True" represents that i-th object shares j-th attribute
        object_names : `list of `str, optional
            Names of objects (rows) of the FormalContext
        attribute_names : `list of `str, optional
            Names of attributes (columns) of the FormalContext
        **kwargs:
            ``description``:
                `str with human readable description of the FormalContext (stored only in json file format)

        """
        self.data = data
        self.object_names = object_names
        self.attribute_names = attribute_names
        self.description = kwargs.get('description')

    @property
    def data(self):
        """Get or set the data with relations between objects and attributes (`list of `list)

        Parameters
        ----------
        value : `list of `list
            value[i][j] represents whether i-th object shares j-th attribute

        Raises
        ------
        AssertionError
            If ``value`` is not a `list
            If ``value`` of type `list is given (should be `list of `list)
            If some lists ``value[i]`` and ``value[j]`` have different length (should be the same for any ``value[i]``)
            If any ``value[i][j]`` is not of type `bool

        """
        return self._data

    @data.setter
    def data(self, value):
        if value is None:
            self._data = None
            self._n_objects = None
            self._n_attributes = None
            return

        assert isinstance(value, list), 'FormalContext.data.setter: "value" should have type "list"'
        assert len(value) > 0, 'FormalContext.data.setter: "value" should have length > 0 (use [[]] for the empty data)'

        length = len(value[0])
        for g_ms in value:
            assert len(g_ms) == length,\
                'FormalContext.data.setter: All sublists of the "value" should have the same length'
            for m in g_ms:
                assert type(m) == bool, 'FormalContext.data.setter: "Value" should consist only of boolean number'

        self._data = value
        self._n_objects = len(value)
        self._n_attributes = length

    @property
    def object_names(self):
        """Get of set the names of the objects in the context

        Parameters
        ----------
        value : `list of `str
            The list of names for the objects (default are '0','1',...,'`n_objects`-1')

        Raises
        ------
        AssertionError
            If the number of names in the ``value`` does not equal to the number of objects in the context
            If the the elements of ``value`` are not of type str

        """
        return self._object_names

    @object_names.setter
    def object_names(self, value):
        if value is None:
            self._object_names = [str(idx) for idx in range(self.n_objects)] if self.data is not None else None
            return

        assert len(value) == len(self._data),\
            'FormalContext.object_names.setter: Length of "value" should match length of data'
        assert all(type(name) == str for name in value),\
            'FormalContext.object_names.setter: Object names should be of type str'
        self._object_names = value

    @property
    def attribute_names(self):
        """Get of set the names of the attributes in the context

        Parameters
        ----------
        value : `list of `str
            The list of names for the attributes (default are "0","1",...,"`n_attributes`-1")

        Raises
        ------
        AssertionError
            If the number of names in the ``value`` does not equal to the number of attributes in the context
            If the the elements of ``value`` are not of type str

        """
        return self._attribute_names

    @attribute_names.setter
    def attribute_names(self, value):
        if value is None:
            self._attribute_names = [str(idx) for idx in range(self.n_attributes)] if self.data is not None else None
            return

        assert len(value) == len(self._data[0]),\
            'FormalContext.attribute_names.setter: Length of "value" should match length of data[0]'
        assert all(type(name) == str for name in value),\
            'FormalContext.object_names.setter: Object names should be of type str'
        self._attribute_names = value

    def extension_i(self, attribute_indexes):
        """Return indexes of maximal set of objects which share given ``attribute_indexes``

        Parameters
        ----------
        attribute_indexes : `list of `int
            Indexes of the attributes (from [0, ``n_attributes``-1])

        Returns
        -------
        extension_indexes : `list of `int
            Indexes of maximal set of objects which share ``attributes``

        """
        return [g_idx for g_idx, g_ms in enumerate(self._data)
                if all([g_ms[m] for m in attribute_indexes])]

    def intention_i(self, object_indexes):
        """Return indexes of maximal set of attributes which are shared by given ``object_indexes`

        Parameters
        ----------
        object_indexes : `list of `int
            Indexes of the objects (from [0, ``n_objects``-1])

        Returns
        -------
        intention_i : `list of `int
            Indexes of maximal set of attributes which are shared by ``objects``

        """
        return [m_idx for m_idx in range(len(self._data[0]))
                if all([self._data[g_idx][m_idx] for g_idx in object_indexes])]

    def intention(self, objects):
        """Return maximal set of attributes which are shared by given ``objects``

        Parameters
        ----------
        objects : `list of `str
            Names of the objects (subset of ``object_names``)

        Returns
        -------
        intention: `list of `str
            Names of maximal set of attributes which are shared by given ``objects``
        """
        obj_idx_dict = {g: g_idx for g_idx, g in enumerate(self._object_names)}
        obj_indices = []
        for g in objects:
            try:
                obj_indices.append(obj_idx_dict[g])
            except KeyError as e:
                raise KeyError(f'FormalContext.intention: Context does not have an object "{g}"')

        intention_i = self.intention_i(obj_indices)
        intention = [self._attribute_names[m_idx] for m_idx in intention_i]
        return intention

    def extension(self, attributes):
        """Return maximal set of objects which share given ``attributes``

        Parameters
        ----------
        attributes : `list of `str
            Names of the attributes (subset of ``attribute_names``)

        Returns
        -------
        extension : `list of `str
            Names of the maximal set of objects which share given ``attributes``

        """
        attr_idx_dict = {m: m_idx for m_idx, m in enumerate(self._attribute_names)}
        attr_indices = []
        for m in attributes:
            try:
                attr_indices.append(attr_idx_dict[m])
            except KeyError as e:
                raise KeyError(f'FormalContext.extension: Context does not have an attribute "{m}"')

        extension_i = self.extension_i(attr_indices)
        extension = [self._object_names[g_idx] for g_idx in extension_i]
        return extension

    @property
    def n_objects(self):
        """Get the number of objects in the context (i.e. len(`data`))"""
        return self._n_objects

    @property
    def n_attributes(self):
        """Get the number of attributes in the context (i.e. len(`data[0]`)"""
        return self._n_attributes

    @property
    def description(self):
        """Get or set the human readable description of the context

        JSON is the only file format to store this information.
        The description will be lost when saving context to .cxt or .csv

        Parameters
        ----------
        value : `str, None
            The human readable description of the context

        Raises
        ------
        AssertionError
            If the given ``value`` is not None and not of type `str

        """
        return self._description

    @description.setter
    def description(self, value):
        assert isinstance(value, (type(None), str)), 'FormalContext.description: Description should be of type `str`'

        self._description = value

    def to_cxt(self, path=None):
        """Convert the FormalContext into cxt file format (save if ``path`` is given)

        Parameters
        ----------
        path : `str or None
            Path to save a context

        Returns
        -------
        context : `str
            If ``path`` is None, the string with .cxt file data is returned. If ``path`` is given - return None

        """
        from fcapy.context.converters import write_cxt
        return write_cxt(self, path)

    def to_json(self, path=None):
        """Convert the FormalContext into json file format (save if ``path`` is given)

        Parameters
        ----------
        path : `str or None
            Path to save a context

        Returns
        -------
        context : `str
            If ``path`` is None, the string with .json file data is returned. If ``path`` is given - return None

        """
        from fcapy.context.converters import write_json
        return write_json(self, path)

    def to_csv(self, path=None, **kwargs):
        """Convert the FormalContext into csv file format (save if ``path`` is given)

        Parameters
        ----------
        path : `str or None
            Path to save a context
        **kwargs :
            ``sep`` : `str
                Field delimiter for the output file
            ``word_true`` : `str
                A placeholder to put instead of 'True' for data[i][j]==True (default 'True')
            ``word_false`` : `str
                A placeholder to put instead of 'False' for data[i][j]==False (default 'False')

        Returns
        -------
        context : `str
            If ``path`` is None, the string with .csv file data is returned. If ``path`` is given - return None

        """
        from fcapy.context.converters import write_csv
        return write_csv(self, path=path, **kwargs)

    def to_pandas(self):
        """Convert the FormalContext into pandas.DataFrame object

        Returns
        -------
        df : pandas.DataFrame
            The dataframe with boolean variables,
            ``object_names`` turned into ``df.index``, ``attribute_names`` turned into ``df.columns``

        """
        from fcapy.context.converters import to_pandas
        return to_pandas(self)

    @staticmethod
    def from_pandas(dataframe):
        # TODO: add docstring
        from fcapy.context.converters import from_pandas
        return from_pandas(dataframe)

    def __repr__(self):
        data_to_print = f'FormalContext ' +\
                        f'({self.n_objects} objects, {self.n_attributes} attributes, ' +\
                        f'{sum([sum(l) for l in self.data])} connections)\n'
        data_to_print += self.print_data(max_n_objects=20, max_n_attributes=10)
        return data_to_print

    def print_data(self, max_n_objects=20, max_n_attributes=10):
        """Get the FormalContext date in the string formatted as the table

        Parameters
        ----------
        max_n_objects : `int
            Maximal number of objects to print. If it is less then ``n_objects`` then print ``max_n_objects/2``
            objects from the "top" and the "bottom" of the context
        max_n_attributes : `int
            Maximal number of attributes to print. If it is less then ``n_attributes`` then print ``max_n_attributes/2``
            attributes from the "left" and the "right" part of the context

        Returns
        -------
        data_to_print : `str
            A string with the context data formatted as the table

        """
        objs_to_print = self.object_names
        attrs_to_print = self.attribute_names
        data_to_print = self.data
        plot_objs_line = False

        if self.n_attributes > max_n_attributes:
            attrs_to_print = attrs_to_print[:max_n_attributes//2]\
                             + ['...'] + attrs_to_print[-max_n_attributes//2:]
            data_to_print = [line[:max_n_attributes//2]+['...']+line[-max_n_attributes//2:] for line in data_to_print]

        if self.n_objects > max_n_objects:
            objs_to_print = objs_to_print[:max_n_objects//2] + objs_to_print[-max_n_objects//2:]
            data_to_print = data_to_print[:max_n_objects//2] + data_to_print[-max_n_objects//2:]
            plot_objs_line = True

        max_obj_name_len = max([len(g) for g in objs_to_print])

        header = ' ' * max_obj_name_len + '|'
        header += '|'.join([m for m in attrs_to_print])
        header += '|'

        lines = []
        for idx in range(len(data_to_print)):
            g_name = objs_to_print[idx]
            g_ms = data_to_print[idx]

            if plot_objs_line and idx == max_n_objects//2:
                line = '.' * (max_obj_name_len + 1 + sum([len(m) + 1 for m in attrs_to_print]))
                lines += [line] * 2

            line = g_name + ' ' * (max_obj_name_len - len(g_name)) + '|'
            line += '|'.join([(' ' * (len(m_name) - 1) + ('X' if m_val else ' ')) if m_val != '...' else '...'
                              for m_name, m_val in zip(attrs_to_print, g_ms)])
            line += '|'
            lines.append(line)

        data_to_print = '\n'.join([header] + lines)
        return data_to_print

    def __eq__(self, other):
        """Wrapper for the comparison method __eq__"""
        if not self.object_names == other.object_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different object_names')

        if not self.attribute_names == other.attribute_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different attribute_names')

        is_equal = self.data == other.data
        return is_equal

    def __ne__(self, other):
        """Wrapper for the comparison method __ne__"""
        if not self.object_names == other.object_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different object_names')

        if not self.attribute_names == other.attribute_names:
            raise ValueError('Two FormalContext objects can not be compared since they have different attribute_names')

        is_not_equal = self.data != other.data
        return is_not_equal

    def __hash__(self):
        return hash((tuple(self._object_names), tuple(self._attribute_names),
                     tuple([tuple(row) for row in self._data])))
