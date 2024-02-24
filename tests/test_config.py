import pytest

import pianoman
from pianoman import Config

import os

class TestConfig:
    def test_default_options_without_default_values_are_None(self, tmpdir):
        config_spec=[{'name':'p','type':'int'}]
        orig_config=Config._default_config
        try:
            Config._default_config=config_spec
            assert( Config().get('p') is None)
            assert( Config().p is None)
        finally:
            Config._default_config=orig_config

    def test_config_field_as_property(self):
        it=pianoman.get_config( conf={"fish":"trout"} )
        assert it.fish == "trout"

    def test_environment_export(self):
        try:
            it=pianoman.get_config( conf={"fish":"trout"} )
            for k,v in filter( lambda p: p[0].endswith( '_fish'),
                               it.as_environment_dict().items()):
                os.environ[k]=v
            assert( pianoman.get_config().fish == 'trout' )
        finally:
            if 'fish' in os.environ:
                os.environ.pop('fish')

    def test_overrides_configfile_with_environment( self, tmpdir ):
        fname="test_overrides_environment_options_with_configfile.json"
        os.environ["{}fish".format(Config._prefix)]="trout"
        ffix = tmpdir.join(fname).write('{"fish":"perch"}')
        it=pianoman.get_config( fname=os.path.join( tmpdir, fname))
        assert it.fish == "trout"

    def test_overrides_default_with_file(self, tmpdir):
        fname="test_overrides_environment_options_with_configfile.json"
        ffix = tmpdir.join(fname).write('{"cluster_port":"44"}')
        it=Config( fname=os.path.join( tmpdir, fname) )
        assert it.cluster_port == "44"

    def test_overrides_default_with_kvpairs(self, tmpdir):
        it=pianoman.get_config( {'cluster_port':'55'})
        assert it.cluster_port == "55"

    def test_overrides_default_with_environment(self, tmpdir):
        os.environ["{}cluster_port".format(Config._prefix)]="trout"
        it=pianoman.get_config()
        os.environ.pop("{}cluster_port".format(Config._prefix))
        assert it.cluster_port == "trout"

    def test_overrides_environment_with_nvpairs(self):
        fname='test_overrides_configfile_with_nvpairs.json'
        os.environ["{}fish".format(Config._prefix)]="carp"
        it=pianoman.get_config( {"fish":"bass"} )
        assert it.fish == "bass"

    def test_skipsdefault_values_from_file(self, tmpdir):
        orig_config=Config._default_config
        default_config=[{'name':'p','type':'int','default':'-1'}]
        try:
            Config._default_config=default_config
            defaults=Config.make_config(default_config)
            fname="test_skipsdefault_values_from_nvpairs.json"
            ffix = tmpdir.join(fname).write('{"p":99}')
            it=Config( fname=os.path.join( tmpdir,fname))

            assert( it.p == 99)

            it.override(defaults, skipdefaults=True)
            assert( it.p == 99)

            it.override(defaults)
            assert( it.p == defaults.get('p'))
        finally:
            Config._default_config=orig_config


    def test_skips_default_values_from_kvpair(self, tmpdir):
        orig_config=Config._default_config
        default_config=[{'name':'p','type':'int','default':'-1'}]
        try:
            Config._default_config=default_config
            default_config=[{'name':'p','type':'int','default':'-1'}]
            defaults=Config.make_config(default_config)
            it=Config( p=33)

            assert( int(it.p) == 33)

            it.override(defaults, skipdefaults=True)
            assert( int(it.p) == 33)

            it.override(defaults)
            assert( it.p == defaults.get('p'))
        finally:
            Config._default_config=orig_config


    def test_property_can_reference_other_properties_defaults(self, tmpdir):
        orig_config=Config._default_config
        default_config=[{'name':'p','type':'int','default':'-1'}]
        try:
            Config._default_config=default_config
            it=Config( d="{p}", p=7)
            assert( int(it.d) == it.p)
            assert( int(it.get('d')) == it.get('p'))
            assert( int(it['d'])==it['p'])
        finally:
            Config._default_config=orig_config

    def test_property_can_reference_other_properties_configfile(self, tmpdir):
        orig_config=Config._default_config
        default_config=[{'name':'p','type':'int','default':'-1'}]
        try:
            Config._default_config=default_config
            fname="test_property_can_reference_other_properties_configfile.json"
            ffix = tmpdir.join(fname).write('{"p":7,"d":"{p}"}')
            it=Config( fname=os.path.join( tmpdir,fname))

            assert( int(it.d) == it.p)
            assert( int(it.get('d')) == it.get('p'))
            assert( int(it['d'])==it['p'])
        finally:
            Config._default_config=orig_config

    def test_property_can_reference_other_properties_via_splat_operator(self, tmpdir):
        orig_config=Config._default_config
        default_config=[{'name':'p','type':'int','default':'-1'}]
        def splatter( **kwargs):
            assert( int(kwargs['d']) == kwargs['p'])
            assert( int(kwargs.get('d')) == kwargs.get('p'))
        try:
            Config._default_config=default_config
            it=Config( d="{p}", p=7)
            splatter( **it )
        finally:
            Config._default_config=orig_config


    def test_can_load_property_with_ref_not_yet_met_from_file(self, tmpdir):
        orig_config=Config._default_config
        default_config=[{'name':'p','type':'int','default':'-1'}]
        try:
            Config._default_config=default_config
            fname="test_can_load_property_with_ref_not_yet_met_from_file.json"
            ffix = tmpdir.join(fname).write('{"p":7,"d":"{q}"}')
            it=Config( fname=os.path.join( tmpdir,fname))

            with pytest.raises(KeyError):
                it.d
            it['q']=99
            assert( int(it.d) == 99)
        finally:
            Config._default_config=orig_config

    def test_getitem_failover_to_dict( self ):
        with pytest.raises(KeyError):
            Config().__this_doesnt_exist__

    def test_list_type_is_nargs(self, tmpdir):
        orig_config=Config._default_config
        try:
            Config._default_config=[{'name':'p','type':'list','default':'[1,2,3]'}]
            it=pianoman.get_config()
            it.build_argparser()
            assert( it.p == [1,2,3])
            args=vars(it.build_argparser().parse_args(['--p', '4','5','6']))
            assert(args['p']==['4','5','6'])
        finally:
            Config._default_config=orig_config


    #TODO: additional tests confirm all variants of this command line are supported: 
    # add_argument(name or flags...[, action][, nargs][, const][, default][, type][, choices][, required][, help][, metavar][, dest])
