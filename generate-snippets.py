#!/usr/bin/python

import os
import json

dest_prefix = 'snippets.generated'
if not os.path.exists (dest_prefix):
    os.makedirs (dest_prefix)

f = open ('CloudFormationResourceSpecification.json', 'r')
spec = json.load (f)

prop_types = spec['PropertyTypes']

prop_snippets = {}
for key in prop_types.keys ():
    try:
        if "::" in key and "." in key:
            prop_name = key.split ('::')[2]
            primary_name = prop_name.split ('.')[1].lower ()
            qualifier = prop_name.split ('.')[0].lower ()
            secondary_qualifier = key.split("::")[1].lower ()
        else:
            primary_name = key.lower ()
            qualifier = None
            secondary_qualifier = None
    except:
        print "Error parsing property name: {0}".format (key)
        continue

    snippet_name = "{0}".format (primary_name)
    if snippet_name in prop_snippets:
        if prop_snippets[snippet_name] is not None:
            snip_rec = prop_snippets[snippet_name]
            prop_snippets["{1}-{0}".format (snip_rec['primary'], snip_rec['qualifier'])] = snip_rec
            prop_snippets[snippet_name] = None

        snippet_name = "{1}-{0}".format (primary_name, qualifier)
        if snippet_name in prop_snippets:
            snippet_name = "{2}-{1}-{0}".format (primary_name, qualifier, secondary_qualifier)

        if snippet_name in prop_snippets:
            print "Unable to store snippet for property {0}".format (key)
            next

    prop_snippets[snippet_name] = {'primary': primary_name, 'qualifier': qualifier, 'full_name': key, 'spec': prop_types[key]}

# remove empty snippet keys
for key in prop_snippets.keys ():
    if prop_snippets[key] is None:
        prop_snippets.pop (key)

for key in prop_snippets.keys ():
    snippet = prop_snippets[key]
    ins_ctr = 1

    sfile = open ("{0}/{1}.cson".format (dest_prefix, key), 'w')

    sfile.write ("'.source.yaml':\n")
    sfile.write ("  '{0}':\n".format (key))
    sfile.write ("      'prefix': '{0}'\n".format (key))
    sfile.write ("      'body':\"\"\"\n")

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
                sfile.write ("         {0}:                # {1}, list of {2}\n".format (pkey, req_descriptor, value_descriptor))
                sfile.write ("         \t- ${{{0}:{1}}}\n".format (ins_ctr, value_descriptor))
            elif sprop['Type'] == 'Map':
                sfile.write ("         {0}:                # {1}, map of {2}\n".format (pkey, req_descriptor, value_descriptor))
                sfile.write ("         \t${{{0}:{1}_key}}: ${{{2}:{1}_value}}\n".format (ins_ctr, value_descriptor, ins_ctr + 1))
                ins_ctr += 1
            else:
                sfile.write ("         {0}: ${{{1}:{2}}}     # {3}\n".format (pkey, ins_ctr, value_descriptor, req_descriptor))
        else:
            sfile.write ("         {0}: ${{{1}:{2}}}     # {3}\n".format (pkey, ins_ctr, value_descriptor, req_descriptor))

    sfile.write ("\"\"\"")

    sfile.close ()



rsrc_types = spec['ResourceTypes']
rsrc_snippets = {}
# go through and extract unique names for all resource types
for key in rsrc_types.keys ():
    primary_name = key.split ('::')[2].lower ()
    qualifier = key.split ('::')[1].lower ()

    snippet_name = "{0}".format (primary_name)
    # if the name has been seen before then store both the old and new name under qualified names
    if snippet_name in rsrc_snippets:
        if rsrc_snippets[snippet_name] is not None:
            snip_rec = rsrc_snippets[snippet_name]
            rsrc_snippets["{1}-{0}".format (snip_rec['primary'], snip_rec['qualifier'])] = snip_rec
            rsrc_snippets[snippet_name] = None

        snippet_name = "{1}-{0}".format (primary_name, qualifier)

    # store the new snippet record
    rsrc_snippets[snippet_name] = {'primary': primary_name, 'qualifier': qualifier, 'full_name': key, 'spec': rsrc_types[key]}

# remove empty snippet keys
for key in rsrc_snippets.keys ():
    if rsrc_snippets[key] is None:
        rsrc_snippets.pop (key)

for key in rsrc_snippets.keys ():
    snippet = rsrc_snippets[key]
    ins_ctr = 1

    sfile = open ("{0}/{1}.cson".format (dest_prefix, key), 'w')

    sfile.write ("'.source.yaml':\n")
    sfile.write ("  '{0}':\n".format (key))
    sfile.write ("      'prefix': '{0}'\n".format (key))
    sfile.write ("      'body':\"\"\"\n")
    sfile.write ("         ${{{0}:{1}_name}}:\n".format (ins_ctr, key))
    sfile.write ("         \tType: \"{0}\"\n".format (snippet['full_name']))
    sfile.write ("         \tProperties:\n")

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
                sfile.write ("         \t\t{0}:                # {1}, list of {2}\n".format (pkey, req_descriptor, value_descriptor))
                sfile.write ("         \t\t\t- ${{{0}:{1}}}\n".format (ins_ctr, value_descriptor))
            elif sprop['Type'] == 'Map':
                sfile.write ("         \t\t{0}:                # {1}, map of {2}\n".format (pkey, req_descriptor, value_descriptor))
                sfile.write ("         \t\t\t${{{0}:{1}_key}}: ${{{2}:{1}_value}}\n".format (ins_ctr, value_descriptor, ins_ctr + 1))
                ins_ctr += 1
            else:
                sfile.write ("         \t\t{0}: ${{{1}:{2}}}     # {3}\n".format (pkey, ins_ctr, value_descriptor, req_descriptor))
        else:
            sfile.write ("         \t\t{0}: ${{{1}:{2}}}     # {3}\n".format (pkey, ins_ctr, value_descriptor, req_descriptor))

    sfile.write ("\"\"\"")

    sfile.close ()
