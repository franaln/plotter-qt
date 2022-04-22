import os, re
import uuid as _uuid

import ROOT

class RootFile:

    def __init__(self, path):
        self.path = path
        self.name = path.replace(".root", "").split('/')[-1]
        self._file = ROOT.TFile.Open(path)

    def __del__(self):
        #self._file.Close()
        pass

    def __iter__(self):
        for depth, dtype, path, name in self.browse_dir(0, ''):
            yield (depth, dtype, path, name)

    def is_valid(self):
        return True

    def browse_dir(self, depth, parent_name):

        cdir = self._file.GetDirectory(parent_name)
        for key in cdir.GetListOfKeys():
            obj = key.ReadObj()
            name = obj.GetName()

            if parent_name:
                path = parent_name + '/' + name
            else:
                path = name

            if obj.InheritsFrom('TList'):
                continue

            if obj.IsFolder():
                if obj.InheritsFrom('TTree'):

                    yield (depth, 'tree', path, name)

                    tree = self._file.Get(name)
                    for b in tree.GetListOfLeaves():
                        bname = b.GetName()
                        yield (depth+1, 'branch', name + '//' + bname, bname)

                else:
                    yield (depth, 'dir', path, name)

                    for ddepth, dtype, dpath, dname in self.browse_dir(depth+1, name):
                        yield (ddepth, dtype, dpath, dname)

            elif obj.InheritsFrom('TH1'):
                yield (depth, 'hist', path, name)
            elif obj.InheritsFrom('TGraph'):
                yield (depth, 'graph', path, name)
            # TODO: add RooWorkspace support
            else:
                continue

    def get_object_info(self, path):
        pass

    def get_object(self, path, selection=''):

        if ':' in path:
            _, path = path.split(':')

        # tree
        if '//' in path:

            treename, name = path.split('//')

            # tree = ROOT.TTree(treename, '')
            # self._file.GetObject(treename, tree)
            tree = self._file.Get(treename)

            tree.Draw(name+'>>'+name, selection, 'goff')

            #htmp = ROOT.TH1F(hname, hname, 100, 0, 100)
            #tree.Project(hname, name, '')

            htmp = ROOT.gDirectory.Get(name)

            obj = htmp.Clone()

        elif '/' in path:
            dirname, name = path.split('/')
            obj = None

        else:
            # histogram/graph
            obj = self._file.Get(path)

        ROOT.SetOwnership(obj, False)
        try:
            obj.SetDirectory(0)
        except:
            pass

        return obj
