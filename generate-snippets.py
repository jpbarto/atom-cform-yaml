#!/usr/bin/python

import json

f = open ('CloudFormationResourceSpecification.json', 'r')
spec = json.load (f)

rsrc_types = spec['ResourceTypes']
prop_types = spec['PropertyTypes']

snippets = {}

# go through and extract unique names for all resource types
for key in rsrc_types.keys ():
    primary_name = key.split ('::')[2].lower ()
    qualifier = key.split ('::')[1].lower ()

    snippet_name = "{0}".format (primary_name)
    # if the name has been seen before then store both the old and new name under qualified names
    if snippet_name in snippets:
        if snippets[snippet_name] is not None:
            snip_rec = snippets[snippet_name]
            snippets["{1}-{0}".format (snip_rec['primary'], snip_rec['qualifier'])] = snip_rec
            snippets[snippet_name] = None

        snippet_name = "{1}-{0}".format (primary_name, qualifier)

    # store the new snippet record
    snippets[snippet_name] = {'primary': primary_name, 'qualifier': qualifier, 'full_name': key, 'spec': rsrc_types[key]}

# remove empty snippet keys
for key in snippets.keys ():
    if snippets[key] is None:
        snippets.pop (key)

for key in snippets.keys ():
    snippet = snippets[key]
    ins_ctr = 1

    sfile = open ("{0}.cson".format (key), 'w')

    sfile.write ("'.source.yaml':\n")
    sfile.write ("  '{0}':\n".format (key))
    sfile.write ("      'prefix': '{0}'\n".format (key))
    sfile.write ("      'body':\"\"\"\n")
    sfile.write ("          ${{{0}:{1}_name}}:\n".format (ins_ctr, key))
    sfile.write ("              Type: \"{0}\"\n".format (snippet['full_name']))
    sfile.write ("              Properties:\n")

    for pkey in sorted (snippet['spec']['Properties'].iterkeys ()):
        sprop = snippet['spec']['Properties'][pkey]

        ins_ctr += 1

        req_descriptor = 'optional'
        if sprop['Required']:
            req_descriptor = 'required'

        value_descriptor = 'value'
        if 'PrimitiveType' in sprop:
            value_descriptor = sprop['PrimitiveType']

        if 'Type' in sprop:
            if 'ItemType' in sprop:
                value_descriptor = sprop['ItemType']
            elif 'PrimitiveItemType' in sprop:
                value_descriptor = sprop['PrimitiveItemType']
            else:
                value_descriptor = sprop['Type']

            if sprop['Type'] == 'List':
                sfile.write ("                  {0}:                # {1}, list of {2}\n".format (pkey, req_descriptor, value_descriptor))
                sfile.write ("                      - ${{{0}:{1}}}\n".format (ins_ctr, value_descriptor))
            elif sprop['Type'] == 'Map':
                sfile.write ("                  {0}:                # {1}, map of {2}\n".format (pkey, req_descriptor, value_descriptor))
                sfile.write ("                      ${{{0}:{1}_key}}: ${{{2}:{1}_value}}\n".format (ins_ctr, value_descriptor, ins_ctr + 1))
                ins_ctr += 1
            else:
                sfile.write ("                  {0}: ${{{1}:{2}}}     # {3}\n".format (pkey, ins_ctr, value_descriptor, req_descriptor))
        else:
            sfile.write ("                  {0}: ${{{1}:{2}}}     # {3}\n".format (pkey, ins_ctr, value_descriptor, req_descriptor))

    sfile.write ("\"\"\"")

    sfile.close ()
