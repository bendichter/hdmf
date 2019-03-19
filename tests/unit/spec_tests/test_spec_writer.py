import unittest2 as unittest
import os
import datetime

from hdmf.spec.write import NamespaceBuilder
from hdmf.spec.namespace import SpecNamespace, NamespaceCatalog
from hdmf.spec.spec import GroupSpec

class TestNamespaceBuilder(unittest.TestCase):
    NS_NAME = 'test_ns'

    def setUp(self):
        # create a builder for the namespace
        self.ns_name = "mylab"
        self.date = datetime.datetime.now()

        self.ns_builder = NamespaceBuilder(doc="mydoc",
                                      name=self.ns_name,
                                      full_name="My Laboratory",
                                      version="0.0.1",
                                      author="foo",
                                      contact="foo@bar.com",
                                      namespace_cls=SpecNamespace,
                                      date=self.date)

        # create extensions
        ext1 = GroupSpec('A custom DataSeries interface',
                          attributes=[],
                          datasets=[],
                          groups=[],
                          data_type_inc=None,
                          data_type_def='MyDataSeries')

        ext2 = GroupSpec('An extension of a DataSeries interface',
                          attributes=[],
                          datasets=[],
                          groups=[],
                          data_type_inc='MyDataSeries',
                          data_type_def='MyExtendedMyDataSeries')

        # add the extension
        self.ext_source_path = 'mylab.specs.yaml'
        self.ns_builder.add_spec(source=self.ext_source_path, spec=ext1)
        self.ns_builder.add_spec(source=self.ext_source_path, spec=ext2)
        self.ns_builder.add_source(source=self.ext_source_path,
                                   doc='Extensions for my lab',
                                   title='My lab extensions')

        self.namespace_path = 'mylab.namespace.yaml'
        self.ns_builder.export(self.namespace_path)

        # Remember the source files
        self.source_files = ['mylab.specs.yaml', 'mylab.namespace.yaml']

    def tearDown(self):
        if os.path.exists(self.ext_source_path):
            os.remove(self.ext_source_path)
        if os.path.exists(self.namespace_path):
            os.remove(self.namespace_path)
        pass

    def test_export_namespace(self):
        with open(self.namespace_path, 'r') as nsfile:
            nsstr = nsfile.read()
            self.assertTrue(nsstr.startswith("namespaces:\n"))
            self.assertTrue("author: foo\n" in nsstr)
            self.assertTrue("contact: foo@bar.com\n" in nsstr)
            self.assertTrue("date: '%s'\n" % self.date.isoformat() in nsstr)
            self.assertTrue("doc: mydoc\n" in nsstr)
            self.assertTrue("full_name: My Laboratory\n" in nsstr)
            self.assertTrue("name: mylab\n" in nsstr)
            self.assertTrue("schema:\n" in nsstr)
            self.assertTrue("doc: Extensions for my lab\n" in nsstr)
            self.assertTrue("source: mylab.specs.yaml\n" in nsstr)
            self.assertTrue("title: Extensions for my lab\n" in nsstr)
            self.assertTrue("version: 0.0.1\n" in nsstr)

    def test_read_namespace(self):
        ns_catalog = NamespaceCatalog()
        ns_catalog.load_namespaces(self.namespace_path, resolve=True)
        loaded_ns = ns_catalog.get_namespace(self.ns_name)
        self.assertEquals(loaded_ns.doc, "mydoc")
        self.assertEquals(loaded_ns.author, "foo")
        self.assertEquals(loaded_ns.contact, "foo@bar.com")
        self.assertEquals(loaded_ns.full_name, "My Laboratory")
        self.assertEquals(loaded_ns.name, "mylab")
        self.assertEquals(loaded_ns.date, self.date.isoformat())
        self.assertDictEqual(loaded_ns.schema[0], {'doc': 'Extensions for my lab',
                                                   'source': 'mylab.specs.yaml',
                                                   'title': 'Extensions for my lab'})
        self.assertEquals(loaded_ns.version, "0.0.1")

    def test_get_source_files(self):
        ns_catalog = NamespaceCatalog()
        ns_catalog.load_namespaces(self.namespace_path, resolve=True)
        loaded_ns = ns_catalog.get_namespace(self.ns_name)
        self.assertListEqual(loaded_ns.get_source_files(), ['mylab.specs.yaml'])
