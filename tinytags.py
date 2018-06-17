
# Copyright (c) 2017-2018 Steve Horne

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Dreamt up in the summer of 2017

import re
from tinydb import TinyDB, Query

class TinyTagsDB(TinyDB):
    def __init__(self, database):
        super(TinyTagsDB, self).__init__(database)
        
        TinyTagsDB.TAGS = self.table("tags")
        TinyTagsDB.TABS = self.table("tables")
        TinyTagsDB.CELLS = self.table("tablecells")
        TinyTagsDB.DATA = self.table("data")
        TinyTagsDB.TABLE = self
        
    def select(self, string):
        """
        Input:
        String can be a db.select("tagname"), db.select(".tagname"), or db.select("#tagname")
        We can combine tags to create tag lists by using db.select(".tagname and .tagname")
        Logical operaters to combine tags are and, or, xor, not.
        
        Output:
        Either Tag() or TagList()
        """
        
        reg = re.match("([\.\#\&]?)(\w+)\s*(and|or|xor|not)?\s*([\.\#\&]?)(\w*)", string)

        logicalop = None

        if reg.group(3) != None:

            regsplit = re.split("\s+(and|or|xor|not)\s+", string)
            logicalops = regsplit[1:][::2]
            
            if all(x == logicalops[0] for x in logicalops):
                logicalop = logicalops[0]
                
            names = regsplit[0:][::2]
            
        # return Tag or TagList    
        if len(reg.group(1)) == 1 or reg.group(1) == "" and reg.group(3) == None:
            return self._select_single(reg.group(1), reg.group(2))

        elif logicalop != None:
            return self._select_logical(logicalop, *names)
        
    def select_data(self, dataname):
        
        dataeid = self.TABLE.DATA.get(Query().name == dataname).eid
        return Data(eid=dataeid)
          
    def _select_single(self, tagclass=None, tagname=None):
        """
        Input: _select_single(tagname="tagname")
        Output: Tag() matches a mix of categories and data.

        Input: _select_single(".", "tagname")
        Output: Tag() that only matches a categorytype.

        Input: _select_single("#", "tagname")
        Output: Tag() that only matches a datatype.

        Input: _select_single("&", "tagname")
        Output: TableCell()
        """
        
        if tagclass == None or tagclass == "":
            tagtype = None
        elif tagclass == ".":
            tagtype = "taglist"
        elif tagclass == "#":
            tagtype = "datalist"
        elif tagclass == "&":
            tagtype = "cell"

        if tagtype != "cell":
            tag = self.TABLE.TAGS.get(Query().name == tagname)
            return Tag(eid=tag.eid) if tag['tagtype'] == tagtype or tagtype == None and tag != None else None
        
        else:
            tablecell = self.TABLE.CELLS.get(Query().name == name)
            return TableCell(eid=tablecell.eid)

    def _select_logical(self, logicalop, *tagnames):
        """
        Input: 
        _select_logical(logicalop, "nameoftag1", "nameoftag2", ...)
        
        Input takes four strings.
        tagclass can be "", ".", "#"
        logicalop can be "and", "or", "xor", "not"
        
        Output: TagList()
        """
        if logicalop in ["and", "or", "xor", "not"]:
            taglist = TagList([], logicalop)

            for tag in tagnames:
                reg = re.match("([\.\#\&]?)(\w+)", tag)
                gottag = _select_single(reg.group(2), tagclass=reg.group(1))
                taglist.append(gottag)

                return taglist

    def insert_root(self, element):
        
        if isinstance(element, Tag):
            tab = self.TABLE.TAGS
            
        elif isinstance(element, TableCell):
            tab = self.TABLE.CELLS
            
        eid = tab.insert(element.__serialize__())
        
        element.eid = eid
       
    def roots(self):
        """
        Returns all root categories.
        """

        return [Tag(eid=tag.eid) for tag in self.TABLE.TAGS.all() if tag['parenttype'] == None]

    def show_roots(self):

        for root in self.roots():
            print "{}".format(root)

    def save(self):
        pass


class NamedComplex(object):
    """
    A NamedComplex is made up of a name and a Complex.
    """
    
    def __init__(self, name=None, complex=None):
        
        NamedComplex.TABLE = TinyTagsDB
        
        self.name = name
        self.complex = [] if complex == None else complex
        self.parent = False
        self.type = None

    def search(self, filter):
        
        for element in self.complex.elementlist:
            if isinstance(element, NamedComplex):
                if filter in element.name:
                    print element.name
                element.search(filter)
            else:
                if filter in element:
                    print element

    def rename(self, name):
        
        self.name = name
        
        if self.eid is not None:
            
            if isinstance(self, Tag):
                table = self.TABLE.TAGS
                
            elif isinstance(self, TableCell):
                table = self.TABLE.CELLS
                    
            table.update({"name": self.name}, eids=[self.eid])


class Id(object):

    TABLE = TinyTagsDB

    def __init__(self, namedcomplex=None):

        self.namedcomplex = namedcomplex
        self.eid = namedcomplex.eid

    def show(self):
        """
        Return a numbered list of hashtags, categories, complex categories, and tables.
        """

        for key, value in self.namedcomplex.items():
            print "{0}: {1}".format(key, value)
        print "\r"

    def update_type(self, type, table, eid):
        
        if eid == None:
            return None

        table.update({"tagtype": type}, eids=[eid])

        self.sync()

    def update_tag_parent(self, type, upeid, table, eid):

        if eid == None:
            return None

        table.update({"parenttype": type}, eids=[eid])
        
        table.update({"parent": upeid}, eids=[eid])

        self.sync()

    def update_id(self, upeid, table, eid, key, sync=None):
        """
        Inserts upeid into table -> eid -> key, and then syncs the element.
        """

        if upeid == None:
            return None

        e = table.get(eid=eid)[key]
        if upeid not in e:
            e.append(upeid)
            table.update({key: e}, eids=[eid])

            if sync is not None: sync.sync()

    def remove_id(self, upeid, table, eid, key, sync=None):
        """
        Deletes element from selected category in database.
        """
        e = table.get(eid=eid)[key]
        if upeid in e:
            e.remove(upeid)
            table.update({key: e}, eids=[eid])
            
            if sync is not None: sync.sync()

            
class Tag(NamedComplex, Id):
    
    def __init__(self, name=None, taglist=None, datalist=None, eid=None):

        if eid != None:
            namedcomplex = self.TABLE.TAGS.get(eid=eid)

            NamedComplex.__init__(self, namedcomplex['name'])
            Id.__init__(self, namedcomplex)

            self.taglist = namedcomplex['taglist']
            self.datalist = namedcomplex['datalist']
            self.tables = namedcomplex['tables']
            self.tablecells = namedcomplex['tablecells']
            self.parent = namedcomplex['parent']
            self.parenttype = namedcomplex['parenttype']
            self.eid = namedcomplex.eid

            self.__update_type__()

            
        else:
            NamedComplex.__init__(self, name)
            
            self.taglist = taglist if taglist != None else []
            self.datalist = datalist if datalist != None else []
            self.tables = []
            self.tablecells = []
            self.parent = None 
            self.parenttype = None
            self.eid = None

            self.__update_type__()
            
    def __repr__(self):

        return self.displayname

    def __update_type__(self):

        if self.taglist != [] and self.datalist != []:
            self.tagtype = None
            self.hastags = True
            self.displayname = "{0}".format(self.name)
            
        elif self.taglist != []:
            self.tagtype = "taglist"
            self.hastags = True
            self.displayname = ".{0}".format(self.name)
        
        elif self.datalist != []:
            self.tagtype = "datalist"
            self.hastags = False
            self.displayname = "#{0}".format(self.name)

        else:
            self.tagtype = None
            self.hastags = False
            self.displayname = "{0}".format(self.name)
            
        self.update_type(self.tagtype, self.TABLE.TAGS, self.eid)
        
    def __serialize__(self):

        self.dict = {'name': self.name,
                    'taglist': self.taglist,
                    'datalist': self.datalist,
                    'tables': self.tables,
                    'tablecells': self.tablecells,
                    'tagtype': self.tagtype,
                    'parent': self.parent,
                    'parenttype': self.parenttype}

        return self.dict

    def sync(self):

        self.namedcomplex = self.TABLE.TAGS.get(eid=self.eid)

        self.name = self.namedcomplex['name']
        self.taglist = self.namedcomplex['taglist']
        self.datalist = self.namedcomplex['datalist']
        self.tables = self.namedcomplex['tables']
        self.tablecells = self.namedcomplex['tablecells']
        self.tagtype = self.namedcomplex['tagtype']
        self.parent = self.namedcomplex['parent']
        self.parenttype = self.namedcomplex['parenttype']
        
    def show(self):
        
        print self.displayname
        
        try:
            for tag in self.get("^"):
                print " "*4 + "Parent: {0}".format(str(tag))
        except:
            pass
        
        for cell in self.get("&"):
            cell.show(tabs=1)

        for tag in self.get():
            if tag.get("^").eid not in [cell.eid for cell in self.get("&")]:
                print " "*4 + "{}".format(tag)

    def get(self, key=None):
        """
        Returns a list of tags, data, tables, or tablecells.
        """

        if self.namedcomplex is not None:
            if key == "" or key == None:
                return TagList([Tag(eid=id) for id in self.namedcomplex['taglist']])
            
            elif key == ".":
                return TagList(
                    [Tag(eid=id) for id in self.namedcomplex['taglist'] if Tag(eid=id).tagtype == "taglist"])
            
            elif key == "#":
                return TagList(
                    [Tag(eid=id) for id in self.namedcomplex['taglist'] if Tag(eid=id).tagtype == "datalist"])
            
            # To abstraction. Returns a list of parent categories that category belongs to.
            elif key == "^" and self.namedcomplex['parent'] != False:
                if self.parenttype == "tag":
                    return Tag(eid=self.namedcomplex['parent'])
                
                elif self.parenttype == "cell":
                    return TableCell(eid=self.namedcomplex['parent'])
            
            elif key == "x" and self.tables != []:
                return [Table(eid=id) for id in self.namedcomplex['tables']]
            
            # Down to TableCells
            elif key == "&":
                return [TableCell(eid=id) for id in self.namedcomplex['tablecells']]
            
            elif key == "d":
                # Returns the data that is associated with this complex tag.
                return [Data(eid=id) for id in self.namedcomplex['datalist']]
            
    def insert(self, *args):
        """
        If selected gets eid and inserts into complex. If made from Category(),
        enters into database and then enters into complex.
        """

        for element in args:
            
            if isinstance(element, Tag) and element.eid == None:
            
                # Insert HashTag into table hashtags.
                eid = self.TABLE.TAGS.insert(element.__serialize__())

                element.eid = eid

                # Add tag element eid to this tag
                self.update_id(eid, self.TABLE.TAGS, self.eid, "taglist", self)
                
                # Insert this Tag into element tag parent.
                self.update_tag_parent("tag", self.eid, self.TABLE.TAGS, eid)
            
            elif isinstance(element, Data) and element.eid == None:
            
                # Insert Data into table data.
                eid = self.TABLE.DATA.insert(element.__serialize__())
                
                # Add data element eid to this tag
                self.update_id(eid, self.TABLE.TAGS, self.eid, "datalist", self)
                
                # Insert this Tag into element tag parent.
                self.update_id(self.eid, self.TABLE.DATA, eid, "parents")
        
            # Set eid for category or hashtag.
            elif element.eid is not None:

                eid = element.eid

                if isinstance(element, Tag):
                    
                    if element.parenttype == "tag":
                        
                        cell = TableCell(None, TagList([self.eid] + [element.parent]))
                        cell.insert_cell()
                        
                        self.update_tag_parent("cell", cell.eid, self.TABLE.TAGS, eid) 
                        
                    elif element.parenttype == "cell":
                        
                        cell = element.get("^")
                        
                        cell.insert(Tag(eid=self.eid))
                        cell.insert_cell()
                        
                    else:
                        
                        # Add this tag to element parent
                        self.update_tag_parent("tag", self.eid, self.TABLE.TAGS, eid)
 
                    # Add tag element eid to this parent tag
                    self.update_id(eid, self.TABLE.TAGS, self.eid, "taglist", self)

                elif isinstance(element, Data):
                    # Add data element eid to this tag
                    self.update_id(eid, self.TABLE.TAGS, self.eid, "datalist", self)

                    # Add this tag eid into table data element parents.
                    self.update_id(self.eid, self.TABLE.DATA, eid, "parents", element)
                    
        self.__update_type__()

    def remove(self):
        """
        Deletes category and all it's children.
        """

        for cellid in self.taglist:
            Tag(eid=cell).remove()

        for dataid in self.datalist:
            Data(eid=data).remove()

        for tableid in self.tables:
            Table(eid=tableid).remove()
            
        for cellid in self.tablecells:
            TableCell(eid=cellid).remove()

        if self.eid != None:
            self.TABLE.TAGS.remove(eids=[self.eid])

class TagList(list):
    """
    A TagList is made up of several Tags
    """

    def __init__(self, elementlist, op=None):
        
        self[:] = elementlist 
        
        self.setoperator = op
        
    def __repr__(self):
        return "TagList({0})".format(self[:])
    
    def show(self):

        print self

    def get(self, key):
        """
        Returns tables and tablecells that are related to tags in this TagList.

        Input:
        TagList().get(key)
        key is either TagList().get("x") for all tables, 
                      TagList().get(".x") for tables that hold categories, 
                      TagList().get("#x") for tables that hold data,
                      TagList().get("&") for tablecells.

        Logical operaters that are used with you use TinyTagsDB.select()
        will be used to find relations among tags.
        
        Output:
        A list of Table() or TableCell()
        """

        # Get sets of tablecell or table ids for all tags in TagList
        if key == "x":
            sets = [set(tag.tables) for tag in self[:]]
            tagclass = "table"
        elif key == ".x":
            sets = [set(tag.tables) for tag in self[:] if tag.tagtype == "taglist"]
            tagclass = "table"
        elif key == "#x":
            sets = [set(tag.tables) for tag in self[:] if tag.tagtype == "datalist"]
            tagclass = "table"
        elif key == "&":
            sets = [set(tag.tablecells) for tag in self[:] if tag.tagtype == "datalist"]
            tagclass = "cell"

        # Choose set operation and does a set operation on the sets.
        if self.setoperator == "and":
            ids = reduce(lambda x, y: x & y, sets)
        if self.setoperator == "or":
            ids = reduce(lambda x, y: x | y, sets)
        if self.setoperator == "xor":
            ids = reduce(lambda x, y: x ^ y, sets)
        if self.setoperator == "not":
            ids = reduce(lambda x, y: x - y, sets)

        # Return a list of tables or tablecells that match 
        if tagclass == "table":
            return [Table(eid=id) for id in ids]
        elif tagclass == "cell":
            return [TableCell(eid=id) for id in ids]

            
    def join(self):
        """
        To complexity. Returns a complex table of two or more dimensions.
        This applies to the elements and creates a number of complex words
        If a category list is put into a category it becomes a supercategory.
        This applies to the category names and works to better organize
        repeating elemenets in categories and specifiy category names.
        Uses tables and set operations to combine elements. If it affects
        the name then do set operations to merge the elements. This creates
        a table where the table cells are a complex name with a list of
        elements that the class is made up of.
        """
        
        return Table(self).join()

    
class Data(object):

    TABLE = TinyTagsDB
    
    def __init__(self, name=None, description=None, location=None, eid=None):

        if eid != None:
            self.eid = eid
            self.sync()
            
        else:
            self.name = name
            self.description = description
            self.location = location
            self.parents = []
            self.eid = None
        
    def __repr__(self):

        return 'Data("{0}")'.format(self.name)
    
    def __serialize__(self):
        
        self.dict = {'name': self.name,
                    'description': self.description,
                    'location': self.location,
                    'parents': self.parents}
        
        return self.dict

    def sync(self):
        
        self.data = self.TABLE.DATA.get(eid=self.eid)
        
        self.name = self.data['name']
        self.description = self.data['description']
        self.location = self.data['location']
        self.parents = self.data['parents']

    def show(self):
        
        print "Name: {0}\nDescription: {1}\nLocation: {2}\r".format(self.name, self.description, self.location)


class Table(list, Id):
    
    def __init__(self, tags=None, tablecell=None, eid=None):
        
        self.name = ""
        self.eid = None
        self.tablecell = tablecell
        self[:] = [tablecell] if tablecell != None else []
        self.joined = False
        self.type = None

        if tags != None:
            self.categorylist = tags
            self.tags = [category.eid for category in tags]
            self.length = len(self.tags)
            self.categorylisthastags = []
            
            for tag in self.categorylist:
                if tag.hastags == True:
                    self.categorylisthastags.append(tag)
            self.categorylist = self.categorylisthastags
            
            for tag in self.categorylist:
                if tag == self.categorylist[0]:
                    self.name += tag.name
                else:
                    self.name += " x {0}".format(tag.name)
           

        if eid == None:
            try:
                len_match = lambda list, length : len(list) == length
                self.table = self.TABLE.TABS.get((Query().tags.all(self.tags)) & (Query().tags.test(len_match, self.length)))
            except:
                self.table = None
                
        else:
            self.table = self.TABLE.TABS.get(eid=eid)

        if self.table != None:

            self.name = self.table['name']
            self.tags = self.table['tags']
            self[:] = self.table['tablecells']
            self.eid = self.table.eid
            
    def __repr__(self):
        
        return self.name
    
    def __serialize__(self):
        
        tablecells = [tablecell for tablecell in self[:] if tablecell.eid != None]

        self.dict = {'name': self.name,
                    'tags': self.tags,
                    'tablecells': tablecells,
                    'type': self.type}
        
        return self.dict
    
    def sync(self):
        
        self.table = self.TABLE.TABS.get(eid=self.eid)
        
        self.name = self.table['name']
        self.tags = self.table['tags']
        self[:] = self.table['tablecells']
        
    def show(self):
        
        print "Name:", self.name
        print "Tags:", self.tags
        print "Cells:", self[:]
        print "Eid:", self.eid
        
    def _ylength(self):
        
        self.repeateach = []
        self.repeattotal = []

        lengths = []
        for category in self.categorylist:
            lengths.append(len(category.taglist))

        multiply = list(reversed(lengths))
        
        while True:
            multiply.pop()
            if len(multiply) == 0:
                self.repeateach.append(1)
                break
            self.repeateach.append(reduce(lambda x, y: x*y, multiply))
        multiply = list(lengths)
        while True:
            multiply.pop()
            if len(multiply) == 0:
                self.repeattotal.append(1)
                break
            self.repeattotal.append(reduce(lambda x, y: x*y, multiply))
        self.repeattotal = list(reversed(self.repeattotal))
        
        return zip(self.repeateach, self.repeattotal)

    def join(self):

        if self.joined is False:
            
            self.joined = True
            
            ylength = self._ylength()
            l = []
            columns = []
            
            for selectlength, category in zip(range(len(self.categorylist)), self.categorylist):
                categorycomplex = category.taglist
                for element in categorycomplex:
                    l += [element]*ylength[selectlength][0]
                l = l*ylength[selectlength][1]
                columns.append(l)
                l = []
                
            rows = zip(*columns)

            len_match = lambda list, length : len(list) == length
            
            for cell in rows:
                
                c = list(cell)

                # Set table type
                table = self.TABLE.CELLS
                l = TagList(c)

                # Check to see if tablecell already exists in database and put it into the tablecells
                dbcell = table.get((Query().complex.all(c)) & (Query().complex.test(len_match, len(c))))
                if dbcell is not None:
                    tablecell = TableCell(eid=dbcell.eid)
                    tablecell.complex = l
                    table.update({"complex": c}, eids=[dbcell.eid])
                else:
                    tablecell = TableCell(None, TagList(c))

                self.append(tablecell)
            
        return self
    
    def select_cells(self, tag, childtagname):
        """
        Return a row or column of cells.
        
        Input: Table.select_cells(int tag, string childtagname)
        
        If you have four cells
        child1 and child2 are in tag number 1
        child3 and child4 are in tag number 2
            child1 & child3
            child1 & child4
            child2 & child3
            child2 & child4
        Table.select_cells(1, "child1")
        This will return all cells from parent tag 1 with child, "child1"
        So child1 & child3, and child1 & child4
        """
        
        cells = []
        
        for element in self:
            if childtagname == Tag(eid=element.complex[tag-1]).name:
                cells.append(element)
                
        return cells
    
    def insert_table(self):
        
        if self.table == None:
            
            # Insert table into database.
            eid = self.TABLE.TABS.insert(self.__serialize__())
            self.eid = eid

            for tag in self.tags:
                # Insert this table eid into parent categories.
                self.update_id(eid, self.TABLE.TAGS, tag, "tables")

        # Insert new tablecell id into this table.
        if self.tablecell != None and self.table != None:
            self.update_id(self.tablecell, self.TABLE.TABS, self.table.eid, "tablecells", self)
        elif self.tablecell != None and self.table == None:
            self.update_id(self.tablecell, self.TABLE.TABS, eid, "tablecells")

        # If tablecell is in database, Update table to include all eids in tablecells
        # If tablcell has no eid, then update_id will return None
        tablecells = [tablecell.eid for tablecell in self[:]]
        for id in tablecells:
            self.update_id(id, self.TABLE.TABS, self.eid, "tablecells", self)

    def remove(self):

        for cell in self[:]:
            try:
                TableCell(eid=cell).remove()
            except:
                pass

        if self.eid != None:
            self.TABLE.TABS.remove(eids=[self.eid])
    
    def get(self, key):
        
        if key == "^":
            # Returns the parent Tags that Table belongs to.
            return TagList([Tag(eid=id) for id in self.tags])
        
        if key == "&":
            # Returns the table cells.
            if self.joined == True:
                return self[:]
            else:
                return [TableCell(eid=id) for id in self[:]]


class TableCell(NamedComplex, Id):

    def __init__(self, name=None, complex=None, eid=None):
        
        if eid != None:
            self.eid = eid
            self.sync()

        else:
            NamedComplex.__init__(self, name, complex)
            
            self.tags = []

            # if no complex, set type to None
            # else, get all the types of the tags.
            if complex == None:
                self.type = None
            else:
                types = [tag.tagtype for tag in complex if not isinstance(tag, int)]

            # if all tag types are the same, set tablecell type to taglist or datalist,
            # else set tablecell type to mix
            if types != [] and all(x == types[0] for x in types):
                self.type = types[0]
            elif types == []:
                self.type = None
            else:
                self.type = "mix"
                
            self.eid = None

        if self.type == "taglist":
            symbol = "." 
        elif self.type == "datalist":
            symbol = "#"
        else:
            symbol = ""

        if self.name == None:
            self.name = ""
            tags = self.get("^")
            for tag in tags:
                if tag == tags[0]:
                    self.name += tag.name    
                else:
                    self.name += " {0}& {1}".format(symbol, tag.name)
        else:
            self.name += "{0}&{1}".format(symbol, self.name)
            
        self.elementqueue = []
            
    def __repr__(self):
        
        return self.name
        
    def __serialize__(self):
        
        self.dict = {'name': self.name,
                    'complex': self.complex,
                    'tags': self.tags,
                    'type': self.type}
        
        return self.dict
    
    def sync(self):
        self.namedcomplex = self.TABLE.CELLS.get(eid=self.eid)
        self.complex = TagList(self.namedcomplex['complex'])

        Id.__init__(self, self.namedcomplex)
        self.name = self.namedcomplex['name']
        self.tags = self.namedcomplex['tags']
        self.type = self.namedcomplex['type']
        
    def show(self, tabs=0):
        cellstring = ""
        for num, cat in enumerate(self.get("^")):
            if num == 0:
                cellstring += "{}".format(cat)
            else:
                cellstring += " & {}".format(cat)
        print " "*4*tabs + cellstring
        for cat in self.get("^")[1:]:
            print " "*4*(tabs+1) + "Parent: {}".format(cat)
        for cat in self.get("and"):
            print " "*4*(tabs+1) + "{}".format(cat)
        for hash in self.get("dand"):
            print " "*4*(tabs+1) + "{}".format(hash)
        
    def insert(self, element):
        """
        If selected gets eid and inserts into complex. If made from Category(),
        enters into database and then enters into complex.
        """
            
        if element.eid is not None:

            self.elementqueue.append(element)
            
        else:
            raise LookupError("Must use TinyTagsDB.select() to insert Category or HashTag.")

    def insert_cell(self):
        if self.eid == None:
    
            self.eid = self.TABLE.CELLS.insert(self.__serialize__())
            self.elementqueue = TagList([Tag(eid=id) for id in self.complex])

        try:
            for element in self.elementqueue:
                
                # Insert eid of element Tag into this table cell key complex
                self.update_id(element.eid, self.TABLE.CELLS, self.eid, "complex", self)

                # Goto Tag and insert eid for this tablecell into Tag key tablecells.
                self.update_id(self.eid, self.TABLE.TAGS, element.eid, "tablecells", element)
                    
            self.elementqueue = []
            
        except:
            pass
        
        # Lookup Tags of this tablecells, and find tags parent categories.
        tags = TagList([Tag(eid=id).get("^") for id in self.complex])

        # Insert Table
        Table(tags=tags, tablecell=self.eid).insert_table()

    def remove(self):

        if self.eid != None:
            self.TABLE.CELLS.remove(eids=[self.eid])
        
    def get(self, key):
        
        try:
            complex = self.namedcomplex['complex']
        except:
            complex = self.complex
            
        if key == "^":
            # Returns the parent tags that TableCell belong to.
            return TagList([Tag(eid=id) for id in complex])
            
        elif key == ".":
            # To abstraction. Returns a list of categories that the tablecell belong to.
            pass

        elif key == "and":
            # Returns common child categories of tablecell categories.
            if self.type == "taglist":
                sets = [set(Tag(eid=id).taglist) for id in complex]
                # Uses a set operation. Returns a list of data.
                ids = reduce(lambda x, y: x & y, sets)
                return [Tag(eid=id) for id in ids]
            else:
                return []

        elif key == "dand":
            # Returns the data that is associated with this complex tag.
            if self.type == "datalist":
                sets = [set(Tag(eid=id).datalist) for id in complex]
                # Uses a set operation. Returns a list of data.
                dataids = reduce(lambda x, y: x & y, sets)
                return [Data(eid=id) for id in dataids]
            else:
                return []

                            

    


