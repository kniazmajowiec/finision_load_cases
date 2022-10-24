import lxml.etree
import lxml.etree as et
import pandas as pd
from pprint import pprint
from copy import deepcopy
import time


def get_root_from_xml_path(_path: str):
    """ Get root - structure of xml nodes """
    tree2 = et.parse(_path)
    return tree2.getroot()


def find_table(_root, table_name):
    ns = {'s': "http://www.scia.cz"}
    return _root.find(f'.//s:table[@t="{table_name}"]', namespaces=ns)


def which_header_is(_root, table: str, header: str) -> int:
    """ Get the index/number of the header in the xml table.
        The integer that stands next to h{int} when attrib t is equal to given header string

    """
    ns = {'s': "http://www.scia.cz"}
    return int(str(_root.find(f'.//s:table[@t="{table}"]//*[@t="{header}"]', namespaces=ns).tag)
               .replace("{http://www.scia.cz}", '')[1:])


def which_header_is_var_in_subtable(_root, table: str, sub_table_no: int, var: str) -> int:
    """ Get the index/number of the header in the xml subtable of table.
        The integer that stands next to h{int} when attrib t is equal to given var string
    :param _root:
    :param table:
    :param sub_table_no:
    :param var:
    :return:
    """

    ns = {'s': "http://www.scia.cz"}
    return int(str(_root.find(f'.//s:table[@t="{table}"]//s:p{sub_table_no}//*[@t="{var}"]', namespaces=ns).tag)
               .replace("{http://www.scia.cz}", '')[1:])


def find_max_table_index(_root, _table):
    ns = {'s': "http://www.scia.cz"}
    idx = [int(sn.attrib['id']) for sn in _root.findall(f'.//s:table[@t="{_table}"]/s:obj', namespaces=ns)]
    try:
        return max(idx)
    except ValueError:
        return 1


def get_all_nodes(_root):
    ns = {'s': "http://www.scia.cz"}
    _table = "EP_DSG_Elements.EP_StructNode.1"

    coord_z = which_header_is(_root, _table, "Coord Z")
    nodes = [{'Node': el.attrib['nm'],
              'Z': round(float(el.find(f'./s:p{coord_z}', namespaces=ns).attrib['v'].replace(',', '.')), 3)}
             for el in _root.findall(f'.//s:table[@t="{_table}"]/s:obj', namespaces=ns)]
    return pd.DataFrame.from_dict(nodes)


def get_all_beams(_root):
    ns = {'s': "http://www.scia.cz"}
    _table = "EP_DSG_Elements.EP_Beam.1"

    beg_node = which_header_is(_root, _table, "Beg. node")
    beams = [{'Beam': el.attrib['nm'], 'Node':el.find(f'./s:p{beg_node}', namespaces=ns).attrib['n']}
             for el in _root.findall(f'.//s:table[@t="{_table}"]/s:obj', namespaces=ns)]
    return pd.DataFrame.from_dict(beams)


def get_all_slabs(_root):
    ns = {'s': "http://www.scia.cz"}
    _table = "EP_DSG_Elements.EP_Plane.1"

    table_geom = which_header_is(_root, _table, "Table of geometry")
    node = which_header_is_var_in_subtable(_root, _table, table_geom, 'Node')

    slabs = [{'Slab': el.attrib['nm'], 'Node':el.find(f'./s:p{table_geom}//s:p{node}', namespaces=ns).attrib['n']}
             for el in _root.findall(f'.//s:table[@t="{_table}"]/s:obj', namespaces=ns)]
    return pd.DataFrame.from_dict(slabs)


def get_all_load_cases(_root):
    ns = {'s': "http://www.scia.cz"}
    _table = "DataSetScia.EP_LoadCase.1"

    lcs = [{'Load case': obj.attrib['nm'], 'id': obj.attrib['id']}
            for obj in _root.findall(f'.//s:table[@t="{_table}"]/s:obj', namespaces=ns)]
    return pd.DataFrame.from_dict(lcs)


def get_all_loads_dict_by_var(_root, _table, var='nm'):
    """ var: str nm or id"""

    ns = {'s': "http://www.scia.cz"}
    return {el.attrib[var]: el for el in _root.findall(f'.//s:table[@t="{_table}"]/s:obj', namespaces=ns)}


def df_from_ref_loads(_root, _table, ref_elem):
    """ for nodal forces             - DataAddLoad.EP_PointForcePoint.1
        for line loads on beams      - DataAddLoad.EP_LineForceLine.1
        for line loads on slabs edge - DataAddLoad.EP_LineForceSurface.1
        for surface loads on slabs   - DataAddLoad.EP_SurfaceForceSurface.1
        for line loads on slabs      - DataAddLoad.8.00.EP_GeneratedForceSur.1
    """
    ns = {'s': "http://www.scia.cz"}

    lc = which_header_is(_root, _table, 'Load case')
    ref_table = which_header_is(_root, _table, 'Reference Table')
    ref_elem_no = which_header_is_var_in_subtable(_root, _table, ref_table,'Member Name')

    pls = [{'Name': el.attrib['nm'], 'id': el.attrib['id'],
            'LC': el.find(f'./s:p{lc}', namespaces=ns).attrib['n'],
            ref_elem: el.find(f'./s:p{ref_table}//s:p{ref_elem_no}', namespaces=ns).attrib['v']}
           for el in _root.findall(f'.//s:table[@t="{_table}"]/s:obj', namespaces=ns)]

    return pd.DataFrame.from_dict(pls)


def df_from_other_loads(_root, _table):
    """ Free line load
        Free surface loads
    """

    ns = {'s': "http://www.scia.cz"}

    lc = which_header_is(_root, _table, 'Load case')
    geom_table = which_header_is(_root, _table, "Table of geometry")
    coord_z = which_header_is_var_in_subtable(_root, _table, geom_table, "Coord Z")

    pls = [{'Name': el.attrib['nm'], 'id': el.attrib['id'],
            'LC': el.find(f'./s:p{lc}', namespaces=ns).attrib['n'],
            'Z': round(float(el.find(f'./s:p{geom_table}//s:p{coord_z}', namespaces=ns).attrib['v'].replace(',', '.'))
                       , 3)}
           for el in _root.findall(f'.//s:table[@t="{_table}"]/s:obj', namespaces=ns)]

    return pd.DataFrame.from_dict(pls)


def copy_load_element_and_change_lc(elem: lxml.etree.Element, data_dict: dict, last_idx: int) -> lxml.etree.Element:
    ns = {'s': "http://www.scia.cz"}

    new_elem = deepcopy(elem)
    old_name = data_dict["Name"]

    # change Name
    if old_name.endswith('_auto'):
        new_name = '_'.join((old_name, '2'))
    elif old_name.endswith('_auto_2'):
        new_name = old_name[:-1]
    else:
        new_name = '_'.join((old_name, 'auto'))

    new_elem.attrib['nm'] = new_name
    new_elem.attrib['id'] = str(last_idx + 1)
    name_elem = new_elem.find(f'.//*[@v="{data_dict["Name"]}"]')
    name_elem.attrib['v'] = new_name

    # change Load Case to new
    lc_elem = new_elem.find(f'.//*[@n="{data_dict["LC"]}"]')
    lc_elem.attrib["i"] = str(data_dict['id_new'])
    lc_elem.attrib['n'] = str(data_dict['Load case'])
    return new_elem


def del_element(table, _dict):
    obj = et.SubElement(table, "deleteobj")
    obj.set("id", str(_dict['id']))
    obj.set("nm", str(_dict['Name']))

    return obj


if __name__ == '__main__':
    _xml = r'C:\Users\mwozniak\Downloads\TTRI - REV 3.58 - Copy.xml'

    root = get_root_from_xml_path(_xml)

    which_header_is_node(root, "EP_DSG_Elements.EP_Plane.1", 114)
