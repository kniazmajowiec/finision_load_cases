import os
import sys
from pathlib import Path
from xml_extraction import *
from xl_extraction import df_from_named_table_in_xl
from GUI import ask_for_input_files, progressbar, show_exception_and_exit

tables = ("DataAddLoad.EP_PointForcePoint.1", "DataAddLoad.EP_LineForceLine.1", "DataAddLoad.EP_LineForceSurface.1",
          "DataAddLoad.EP_SurfaceForceSurface.1", "DataAddLoad.8.00.EP_GeneratedForceSur.1",
          "DataAddLoad.EP_SurfaceForceFree.1", "DataAddLoad.EP_LineForceFree.1")


if __name__ == '__main__':
    sys.excepthook = show_exception_and_exit
    _xml, xl_file = ask_for_input_files()

    # _xml = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Tour Triangle\Finision load cases\initial test data\second.xml'
    # xl_file = r'C:\Users\mwozniak\OneDrive - BESIX\Desktop\Tour Triangle\Finision load cases\initial test data\FinitionsScriptTest.xlsx'

    root = get_root_from_xml_path(_xml)

    # all geom members
    print('Getting Geometrical data')
    dfn = get_all_nodes(root)  # Nodes
    dfb = get_all_beams(root)  # 1D Members
    dfe = get_all_internal_edges(root)  # internal edges
    dfs = get_all_slabs(root)  # 2D Members

    # join edges and slabs together that's why edges are called Slab in DF
    dfs = pd.concat([dfs, dfe], ignore_index=True)
    # get all load cases
    print('Getting Load Cases')
    df_lc = get_all_load_cases(root)

    # add Z to beams and slabs
    dfb = dfb.merge(dfn)
    dfs = dfs.merge(dfn)

    # all loads
    print('Getting all loads (point, line, surface)')
    nl = df_from_ref_loads(root, "DataAddLoad.EP_PointForcePoint.1", 'Node')  # nodal loads
    llb = df_from_ref_loads(root, "DataAddLoad.EP_LineForceLine.1", 'Beam')  # line loads on beams
    lls = df_from_ref_loads(root, "DataAddLoad.EP_LineForceSurface.1", 'Slab')  # line loads on slabs
    sls = df_from_ref_loads(root, "DataAddLoad.EP_SurfaceForceSurface.1", 'Slab')  # surface loads on slabs
    gls = df_from_ref_loads(root, "DataAddLoad.8.00.EP_GeneratedForceSur.1", 'Slab')  # generate line loads on slabs
    sfl = df_from_other_loads(root, "DataAddLoad.EP_SurfaceForceFree.1")  # surface free loads
    lfl = df_from_other_loads(root, "DataAddLoad.EP_LineForceFree.1")  # line free loads

    # add Z to loads
    nl = nl.merge(dfn)
    llb = llb.merge(dfb)
    lls = lls.merge(dfs)
    sls = sls.merge(dfs)
    gls = gls.merge(dfs)

    # make a dictionary connecting table name and DataFrame
    dfs = (nl, llb, lls, sls, gls, sfl, lfl)
    table_df_dict = {table: _df for table, _df in zip(tables, dfs)}

    # Get data from xl
    print('Getting data from excel')
    df_in = df_from_named_table_in_xl(xl_file, 'LC_to_copy')
    df_out = df_from_named_table_in_xl(xl_file, 'Loads_to_paste')
    # assure that all floats are coma separated
    for col in ['z_inf [m]', 'z_sup [m]']:
        df_out[col] = df_out[col].astype(str).str.replace(',', '.').astype(float)

    # get LCs from which all loads must be deleted
    lc_del = df_out['Load case'].unique()
    # get LCs from which all loads must be copied
    lc_copy = df_in['Load case'].unique()

    # add id for load cases to which loads needs to be copied
    df_out = df_out.merge(df_lc)  # df_lc Name is already called Load case thus do not need to specify column names

    # find out if any load cases were misspelled, thus deleted from the DF and produce the txt file with their names
    missing_lcs = set(lc_del).difference(set(df_out['Load case'].unique()))
    if missing_lcs:
        _txt = str(Path(os.path.join(str(Path(_xml).parent), 'missing load cases.txt')))
        with open(_txt, 'w') as f:
            f.write(str(missing_lcs))

    # loop over table and DataFrames
    for _table, _df in table_df_dict.items():

        # Merge all loads with names of new load cases
        # 1. sort Dataframe to be merge as of
        _df.sort_values('Z', inplace=True)
        df_out.sort_values('z_inf [m]', inplace=True)
        df = pd.merge_asof(_df, df_out, left_on='Z', right_on='z_inf [m]', direction='backward', suffixes=('', '_new'))
        # 2. assure that none of Z are outside the limits
        df = df.loc[(df['z_inf [m]'] < df['Z']) & (df['Z'] < df['z_sup [m]'])]

        # Find loads to be deleted
        df_del = _df.loc[_df['LC'].isin(lc_del)].to_dict('records')
        # Find loads to be copied
        df_copy = df.loc[df['LC'].isin(lc_copy)].to_dict('records')

        # Find xml table to add deleted and copy new elements (loads), its last index and all elements
        table = find_table(root, _table)
        last_idx = find_max_table_index(root, _table)
        xml_load_dict = get_all_loads_dict_by_var(root, _table)

        # remove all old loads
        for load in xml_load_dict.values():
            table.remove(load)

        load_type = _table[_table.index('.EP_')+4: -2]
        print()  # stay not ot overwrite previous message
        # loop over loads to be copied
        for copy_dict in progressbar(df_copy, load_type):
            # print('\n', copy_dict, '\n')

            # find the old load
            old_load = xml_load_dict[copy_dict['Name']]
            # change its name and load case
            new_load = copy_load_element_and_change_lc(old_load, copy_dict, last_idx)
            table.append(new_load)
            # update new last index
            last_idx += 1

        for del_dict in df_del:
            table.append(del_element(table, del_dict))

    # remove nodes, members 1D, members 2D & load cases
    add_tables = ("EP_DSG_Elements.EP_StructNode.1", "EP_DSG_Elements.EP_Beam.1", "EP_DSG_Elements.EP_Plane.1",
                  "DataSetScia.EP_LoadCase.1", "EP_DSG_Elements.EP_SlabInternalEdge.1")

    # Clean xml to make is smaller by deleting objects that do not need to be updated
    print("\nRemoving unnecessary data from the xml")
    for _table in add_tables:
        table = find_table(root, _table)
        all_objs = get_all_objs_from_table(root, _table)
        for obj in all_objs:
            table.remove(obj)

    _xml2 = str(Path(os.path.join(str(Path(_xml).parent), 'new_loads.xml')))
    with open(_xml2, 'w') as f:
        _xml1 = et.tostring(root, pretty_print=True, xml_declaration=True).decode('utf-8')
        f.write(_xml1)
        print(f'xml saved in :{_xml2}')
