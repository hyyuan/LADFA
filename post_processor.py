"""
Post-Processing and Network Visualization Module

This module processes privacy policy analysis results to create network graphs
and statistical analyses. It handles:
- Data flow graph construction from CSV results
- Network analysis (centrality, paths, trees)
- Interactive HTML visualizations using Pyvis
- Statistical metrics and verification sampling
- Entity normalization (singularization, abbreviation handling)

The module supports two main workflows:
1. post_processing() - Full analysis with verification sampling
2. post_processing_simple() - Multiple network metric calculations
"""

import numpy as np
import csv
import json
import networkx as nx
from pyvis.network import Network
import colorsys
import inflect
import re
import spacy

# Load spaCy's English language model for linguistic processing
nlp = spacy.load("en_core_web_sm")


def get_main(phrase):
    """
    Determine the main focus of a phrase.
    Uses linguistic parsing to identify the headword.
    """
    doc = nlp(phrase)
    for token in doc:
        if token.dep_ == "ROOT":  # The root token is often the main focus
            return token.text
    # Fallback: Return the last noun if no root is identified
    nouns = [token.text for token in doc if token.pos_ == "NOUN"]
    return nouns[-1] if nouns else phrase


def get_poss(phrase):
    """
    Determine the main focus of a phrase.
    Uses linguistic parsing to identify the headword.
    """
    doc = nlp(phrase)

    poss_modifiers = [token.text for token in doc if token.dep_ == "poss"]
    return poss_modifiers[-1] if poss_modifiers else phrase



def is_abbreviation(word):
    """
    Detect if a word is likely an abbreviation or acronym.
    - Fully uppercase (e.g., GPS, CCS)
    - Contains numbers (e.g., 4G, H2O)
    - Has special characters (e.g., C++ or R&D)
    """
    return word.isupper() or bool(re.search(r'\d|[&+]', word)) or word.endswith("'s")


def singularize_phrase(phrase, exclusions):
    if phrase not in exclusions:
        # Initialize the inflect engine
        p = inflect.engine()
        # Split the phrase into words
        words = phrase.split()
        # Singularize each word unless it's detected as an abbreviation
        singular_words = [
            word if is_abbreviation(word) or word in exclusions else (p.singular_noun(word) or word)
            for word in words
        ]
        # Join the words back into a string
        return ' '.join(singular_words)
    else:
        return phrase


def get_html_template(page):
    template = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Interactive Network</title>
                <style>
                    body, html {{
                        height: 100%;
                        margin: 0;
                        padding: 0;
                        font-family: Arial, sans-serif;
                    }}
                    #container {{
                        display: flex;
                        height: 100%;
                    }}
                    #network-container {{
                        width: 70%;
                        height: 100%;
                    }}
                    #sidePanel {{
                        width: 30%;
                        height: 100%;
                        padding: 20px;
                        box-sizing: border-box;
                        overflow-y: auto;
                        background-color: #f0f0f0;
                    }}
                </style>
            </head>
            <body>
                <div id="container">
                    <div id="network-container">
                        <iframe id="network-iframe" src="{page}" style="width: 100%; height: 100%; border: none;"></iframe>
                    </div>
                    <div id="sidePanel">
                        <h2>Node Information</h2>
                        <p id="nodeInfo">Click on an edge to see its information here.</p>
                    </div>
                </div>

                <script>

                document.addEventListener("DOMContentLoaded", function() {{
                    var iframe = document.getElementById('network-iframe');
                    var nodeInfo = document.getElementById('nodeInfo');

                    iframe.onload = function() {{
                        var network = iframe.contentWindow.network;
                        network.on("click", function(params) {{
                            // Check if an edge is clicked
                            if (params.edges.length > 0) {{
                                // Get the clicked edge's ID
                                var clickedEdge = network.body.data.edges.get(params.edges[0]);
                                var fromNodeId = clickedEdge.from;
                                var toNodeId = clickedEdge.to;

                                // Get details of the nodes using their IDs
                                var fromNode = network.body.data.nodes.get(fromNodeId);
                                var toNode = network.body.data.nodes.get(toNodeId);


                                // Display the information for the clicked edge and its connected nodes
                                nodeInfo.innerHTML = `
                                            <h3>Connected Nodes</h3>
                                            <p><strong>From Node:</strong> ${{fromNode.label || fromNode.title || "No label available."}}</p>
                                            <p><strong>To Node:</strong> ${{toNode.label || toNode.title || "No label available."}} </p>

                                            <h3>Edge Information</h3>
                                            <p><strong>Edge group:</strong> ${{clickedEdge.group || "No description available."}}</p>
                                            <p><strong>Description:</strong> ${{clickedEdge.description || "No description available."}}</p>
                                            <p><strong>Index:</strong> ${{clickedEdge.index || "No index available."}}</p>

                                            `;

                            }} else {{
                                // Default message when no edge is clicked
                                nodeInfo.innerHTML = "Click on an edge to see its information here.";
                            }}
                        }});

                    }};
                }});

                </script>
            </body>
            </html>
                """
    return template


def generate_distinct_colors(n):
    colors = []
    for i in range(n):
        hue = i / n
        saturation = 0.7
        value = 0.9
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
        )
        colors.append(hex_color)
    return colors


def read_text_segment(csv_file_path):
    text_dictrionary = {}
    with open(csv_file_path, mode='r', newline='', encoding='utf8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row if it exists
        for line_num, row in enumerate(csv_reader, 2):
            idx = row[0]
            text = row[1]
            text_dictrionary[idx] = text
    return text_dictrionary


def load_json_data(json_string):
    parsed_data = None
    # Step 1: Remove outer single quotes if present
    if json_string.startswith("'") and json_string.endswith("'"):
        json_string = json_string.strip("'")

    # Step 2: Strip leading/trailing whitespace
    json_string = json_string.strip()

    # Step 3: Parse the cleaned JSON
    try:
        parsed_data = json.loads(json_string)
        if isinstance(parsed_data, dict):
            return parsed_data
        else:
            if parsed_data.startswith("'") and parsed_data.endswith("'"):
                parsed_data = parsed_data.strip("'")
            parsed_data = parsed_data.strip()
            parsed_data = json.loads(parsed_data)
            return parsed_data

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return parsed_data


def rectify_collection_party(entity):
    flag = False
    first_party_entity_arr = ["we", "us", "this website", "this company", "this organisation",
                              "this organization", "this app", "from you", "our website", "our",
                              "our company", "our organisation", "our organization", "our service",
                              "our app", "the website", "the company", "the app", "the organization",
                              "app", "device", "your app", "your device", "the device", "your car", "car"]

    first_party_entity_main_root_arr = ["we", "We", "us", "Website", "website", "Company", "company", "Organisation", "organisation", "Organization", "organization",
                                        "App", "app", "Service", "service", "Device", "device", "Car", "car", "Site", "site"]
    first_party_entity_poss_arr = ["this", "our", "This", "Our"]
    for item in first_party_entity_arr:
        if entity == item:
            flag = True
            break
        else:
            for item_root in first_party_entity_main_root_arr:
                main_entity = get_main(entity)
                for item_poss in first_party_entity_poss_arr:
                    pos_entity = get_poss(entity)
                    if main_entity == item_root and pos_entity == item_poss:
                        flag = True
                        break
    return flag


def get_entity_property(entity, party_category, main_party, first_party_arr, third_party_arr, user_party_arr):
    entity = entity.lower()
    if entity != "":
        if entity.find(main_party) >= 0:
            if entity not in first_party_arr:
                first_party_arr.append(entity)
            entity_color = "#ccff99"
        else:
            if rectify_collection_party(entity):
                if entity not in first_party_arr:
                    first_party_arr.append(entity)
                entity_color = "#ccff99"
            else:
                main_part = get_main(entity)
                if main_part.startswith('you') or main_part.startswith('user') or main_part.startswith('customer'):
                    entity_color = "#f7ff99"
                    if entity not in user_party_arr:
                        user_party_arr.append(entity)
                else:
                    if party_category == "Unspecified" and entity == 'unspecified party':
                        entity_color = "#00008B"
                    else:
                        if entity not in third_party_arr:
                            third_party_arr.append(entity)
                        entity_color = "#ff99ff"
    else:
        entity_color = "#00008B"

    return entity_color, first_party_arr, third_party_arr, user_party_arr


def remove_spaces(text):
    if text[0] == ' ':
        text = text[1:]
    if text[:] == ' ':
        text = text[0:len(text)-2]
    return text


def get_abbreviation(text, abbreviation_dict):

    import re
    tmp = re.findall(r'\(([^)]+)\)', text)
    processed_text = text
    if len(tmp) == 1:
        text_brackets = tmp[0]
        tmp_arr = text_brackets.split()
        pos_1 = text.find('(')
        pos_2 = text.find(')')
        sub_string_1 = text[0:pos_1-1]
        sub_string_2 = text[pos_2+1:]

        if len(tmp_arr) == 1:
            abbreviation = tmp_arr[0]
            sub_string_1_arr = sub_string_1.split()
            abbreviation_len = len(abbreviation)
            if len(sub_string_1_arr)-abbreviation_len >= 0:
                temp_string_arr = sub_string_1_arr[len(sub_string_1_arr)-abbreviation_len:len(sub_string_1_arr)+1]
                item_arr = []
                for item in temp_string_arr:
                    item_arr.append(item[0])
                sub_string_1_abbreviation = ''.join(item_arr)
                sub_string_1_full = ' '.join(temp_string_arr)
                sub_string_1_full = remove_spaces(sub_string_1_full)

                if abbreviation == sub_string_1_abbreviation:
                    processed_text = text.replace('(', '')
                    processed_text = processed_text.replace(')', '')
                    processed_text = processed_text.replace(abbreviation, '')
                    if abbreviation not in abbreviation_dict:
                        abbreviation_dict[abbreviation] = sub_string_1_full
                    processed_text = remove_spaces(processed_text)

            sub_string_2_arr = sub_string_2.split()
            abbreviation_len = len(abbreviation)
            if len(sub_string_2_arr) >= abbreviation_len:
                temp_string_arr = sub_string_2_arr[0:abbreviation_len]
                item_arr = []
                for item in temp_string_arr:
                    item_arr.append(item[0])
                sub_string_2_abbreviation = ''.join(item_arr)
                sub_string_2_full = ' '.join(temp_string_arr)
                sub_string_2_full = remove_spaces(sub_string_2_full)
                if abbreviation == sub_string_2_abbreviation:
                    if abbreviation not in abbreviation_dict:
                        abbreviation_dict[abbreviation] = sub_string_2_full
                    processed_text = text.replace('(', '')
                    processed_text = processed_text.replace(')', '')
                    processed_text = processed_text.replace(abbreviation, '')
                    processed_text = remove_spaces(processed_text)

        elif len(tmp_arr) > 1:
            item_arr = []
            for item in tmp_arr:
                item_arr.append(item[0])
            abbreviation = ''.join(item_arr)

            pos_1 = text.find('(')
            pos_2 = text.find(')')
            sub_string_1 = text[0:pos_1 - 1]
            sub_string_2 = text[pos_2 + 1:]

            print(sub_string_1)
            sub_string_1_arr = sub_string_1.split()
            print(sub_string_1_arr)
            if len(sub_string_1_arr) > 0:
                sub_string_1_abbreviation = sub_string_1_arr[len(sub_string_1_arr)-1]
                if abbreviation == sub_string_1_abbreviation:
                    if abbreviation not in abbreviation_dict:
                        abbreviation_dict[abbreviation] = sub_string_1
                    processed_text = text.replace('(', '')
                    processed_text = processed_text.replace(')', '')
                    processed_text = processed_text.replace(sub_string_1, '')
                    processed_text = remove_spaces(processed_text)

            print(sub_string_2)
            sub_string_2_arr = sub_string_2.split()
            print(sub_string_2_arr)
            if len(sub_string_2_arr) > 0:
                sub_string_2_abbreviation = sub_string_2_arr[len(sub_string_2_arr)-1]
                if abbreviation == sub_string_2_abbreviation:
                    if abbreviation not in abbreviation_dict:
                        abbreviation_dict[abbreviation] = sub_string_2
                    processed_text = text.replace('(', '')
                    processed_text = processed_text.replace(')', '')
                    processed_text = processed_text.replace(sub_string_2, '')
                    processed_text = remove_spaces(processed_text)
    return processed_text, abbreviation_dict


def get_data_flow_graph_revised(input_file, main_party, csv_file):
    text_dictrionary = read_text_segment(csv_file)
    data_color = '#99ccff'
    abbreviation_dict = {}

    # Create a NetworkX graph
    G = nx.MultiDiGraph()

    first_party_arr = []
    third_party_arr = []
    user_party_arr = []

    data_flow_completed_arr = []
    data_flow_no_sender_arr = []
    data_flow_no_receiver_arr = []
    data_category_dic = {}
    data_output_arr = []

    exclusions = ['Our', 'our', 'we', 'We', 'us', 'Us', 'They', 'they', 'Them', 'them', 'data', 'Data', 'address',
                  'Address', 'as', 'As', 'are', 'Are', 'is', 'Is', 'whether', 'Whether', 'another', 'Another',
                  'Have', 'have', 'Has', 'has', 'The', 'the']
    # Open and read the JSON file
    with open('kb/data_processing_purpose_kt.json', 'r') as file:
        _data = json.load(file)
        purposes = []
        purpose_data = _data['DataTypes']
        for item in purpose_data:
            purposes.append(item['name'])

    purpose_colors = generate_distinct_colors(len(purposes))
    purpose_color_map = dict(zip(purposes, purpose_colors))

    with open(input_file, 'r', encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header row if it exists

        for line_num, row in enumerate(csvreader, 2):
            print("row ", row)
            data_output = []
            raw_idx = row[0]
            raw_text = text_dictrionary[raw_idx]
            data_output.append(raw_text)
            data_type = row[1]

            data_category_json = load_json_data(row[2])
            data_flow_json = load_json_data(row[3])
            data_collection_party_json = load_json_data(row[4])
            data_collection_purpose_json = load_json_data(row[5])
            data_collection_method_json = load_json_data(row[6])

            data_category = ""
            if data_category_json is not None:
                if len(data_category_json['Output']) > 0:
                    for item in data_category_json['Output']:
                        data_category = item['DataCategory']
                else:
                    data_category = 'Unspecified'

            if data_type not in data_category_dic:
                data_category_dic[data_type] = data_category

            data_sender = ''
            data_receiver = ''
            if len(data_flow_json['data']) > 0:
                for item in data_flow_json['data']:
                    data_sender = item['data_sender']
                    data_receiver = item['data_receiver']

            data_type = singularize_phrase(data_type, exclusions)
            data_sender = singularize_phrase(data_sender, exclusions)
            data_receiver = singularize_phrase(data_receiver, exclusions)

            data_type = data_type.lower()
            data_sender = data_sender.lower()
            data_receiver = data_receiver.lower()

            data_type = data_type.replace('the', '')
            data_sender = data_sender.replace('the', '')
            data_receiver = data_receiver.replace('the', '')

            data_type, abbreviation_dict = get_abbreviation(data_type, abbreviation_dict)
            data_sender, abbreviation_dict = get_abbreviation(data_sender, abbreviation_dict)
            data_receiver, abbreviation_dict = get_abbreviation(data_receiver, abbreviation_dict)

            if len(data_type)>0:
                data_type = remove_spaces(data_type)
            if len(data_sender) > 0:
                data_sender = remove_spaces(data_sender)
            if len(data_receiver) > 0:
                data_receiver = remove_spaces(data_receiver)

            if data_sender != data_type and data_receiver != data_type and data_sender != data_receiver:
                if data_sender != '' and data_receiver != '':
                    tmp = data_sender + '#' + data_type + '#' + data_receiver
                    if tmp not in data_flow_completed_arr:
                        data_flow_completed_arr.append(data_sender + '#' + data_type + '#' + data_receiver)
                if data_sender == '' and data_receiver != '':
                    tmp = data_sender + '#' + data_type + '#' + data_receiver
                    if tmp not in data_flow_no_sender_arr:
                        data_flow_no_sender_arr.append(data_sender + '#' + data_type + '#' + data_receiver)
                if data_sender != '' and data_receiver == '':
                    tmp = data_sender + '#' + data_type + '#' + data_receiver
                    if tmp not in data_flow_no_receiver_arr:
                        data_flow_no_receiver_arr.append(data_sender + '#' + data_type + '#' + data_receiver)

                data_collection_party = ""
                if len(data_collection_party_json['Output']) > 0:
                    data_collection_party = data_collection_party_json['Output'][0]['DataCategory']
                    if data_receiver.find(main_party) >= 0:
                        data_collection_party = 'First Party'
                    else:
                        if rectify_collection_party(data_receiver):
                            data_collection_party = 'First Party'

                data_collection_purpose = ""

                if len(data_collection_purpose_json['Output']) > 0:
                    for item in data_collection_purpose_json['Output']:
                        data_collection_purpose += item['DataCategory'] + '; '

                data_collection_method = ""
                if len(data_collection_method_json['Output']) > 0:
                    for item in data_collection_method_json['Output']:
                        reference_text = item['InputText']
                        if data_type in reference_text:
                            data_collection_method = item['DataCategory']
                    if data_collection_method == "":
                        data_collection_method = data_collection_method_json['Output'][0]['DataCategory']

                # Define entity color
                data_sender_entity_color, first_party_arr, third_party_arr, user_party_arr = get_entity_property(
                    data_sender, data_collection_party, main_party,
                    first_party_arr, third_party_arr, user_party_arr)
                data_receiver_entity_color, first_party_arr, third_party_arr, user_party_arr = get_entity_property(
                    data_receiver, data_collection_party, main_party,
                    first_party_arr, third_party_arr, user_party_arr)

                if data_collection_purpose in purpose_color_map:
                    purpose_color = purpose_color_map[data_collection_purpose]
                else:
                    purpose_color = "ff000000"

                if not G.has_node(data_sender):
                    if data_sender == "":
                        G.add_node(data_sender, color=data_sender_entity_color, size=40, title="unknown")
                    else:
                        G.add_node(data_sender, color=data_sender_entity_color, size=40, title=data_sender)
                if not G.has_node(data_type) and data_type != "":
                    G.add_node(data_type, color=data_color, size=20, title=data_type, shape='box')
                if not G.has_node(data_receiver):
                    G.add_node(data_receiver, color=data_receiver_entity_color, size=40, title=data_receiver)
                if not G.has_edge(data_sender, data_type):
                    G.add_edge(data_sender, data_type, group=raw_idx, color=purpose_color, description=raw_text,
                               title=data_collection_purpose, arrows="to")
                if not G.has_edge(data_type, data_receiver):
                    G.add_edge(data_type, data_receiver, group=raw_idx, color=purpose_color, description=raw_text,
                               title=data_collection_purpose, arrows="to")

                data_output.append(data_type)
                data_output.append(data_category)
                data_output.append(data_sender)
                data_output.append(data_receiver)
                data_output.append(data_collection_party)
                data_output.append(data_collection_purpose)
                data_output.append(data_collection_method)
                data_output_arr.append(data_output)

    return G, data_category_dic, first_party_arr, third_party_arr, user_party_arr, data_flow_completed_arr, data_flow_no_sender_arr, data_flow_no_receiver_arr, data_output_arr



def get_data_flow_graph_simple(input_file, main_party, csv_file):
    text_dictrionary = read_text_segment(csv_file)
    data_color = '#99ccff'
    abbreviation_dict = {}

    # Create a NetworkX graph
    G = nx.MultiDiGraph()

    # Open and read the JSON file
    with open('kb/data_processing_purpose_kt.json', 'r') as file:
        _data = json.load(file)

    exclusions = ['Our', 'our', 'we', 'We', 'us', 'Us', 'They', 'they', 'Them', 'them', 'data', 'Data', 'address',
                  'Address', 'as', 'As', 'are', 'Are', 'is', 'Is', 'whether', 'Whether', 'another', 'Another',
                  'Have', 'have', 'Has', 'has', 'The', 'the']

    with open(input_file, 'r', encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header row if it exists

        for line_num, row in enumerate(csvreader, 2):
            print("row ", row)
            data_output = []
            raw_idx = row[0]
            raw_text = text_dictrionary[raw_idx]
            data_output.append(raw_text)
            data_type = row[1]

            data_category_json = load_json_data(row[2])
            data_flow_json = load_json_data(row[3])
            data_collection_party_json = load_json_data(row[4])
            data_collection_purpose_json = load_json_data(row[5])
            data_collection_method_json = load_json_data(row[6])

            data_category = ""
            if data_category_json is not None:
                if len(data_category_json['Output']) > 0:
                    for item in data_category_json['Output']:
                        data_category = item['DataCategory']
                else:
                    data_category = 'Unspecified'

            data_sender = ''
            data_receiver = ''
            if len(data_flow_json['data']) > 0:
                for item in data_flow_json['data']:
                    data_sender = item['data_sender']
                    data_receiver = item['data_receiver']

            data_type = singularize_phrase(data_type, exclusions)
            data_sender = singularize_phrase(data_sender, exclusions)
            data_receiver = singularize_phrase(data_receiver, exclusions)

            data_type = data_type.lower()
            data_sender = data_sender.lower()
            data_receiver = data_receiver.lower()

            data_type = data_type.replace('the', '')
            data_sender = data_sender.replace('the', '')
            data_receiver = data_receiver.replace('the', '')

            data_type, abbreviation_dict = get_abbreviation(data_type, abbreviation_dict)
            data_sender, abbreviation_dict = get_abbreviation(data_sender, abbreviation_dict)
            data_receiver, abbreviation_dict = get_abbreviation(data_receiver, abbreviation_dict)

            if len(data_type)>0:
                data_type = remove_spaces(data_type)
            if len(data_sender) > 0:
                data_sender = remove_spaces(data_sender)
            if len(data_receiver) > 0:
                data_receiver = remove_spaces(data_receiver)

            if data_sender != data_type and data_receiver != data_type and data_sender != data_receiver:
                if not G.has_node(data_sender):
                    if data_sender == "":
                        G.add_node(data_sender, size=40, title="unknown")
                    else:
                        G.add_node(data_sender, size=40, title=data_sender)
                if not G.has_node(data_type) and data_type != "":
                    G.add_node(data_type, color=data_color, size=20, title=data_type, shape='box')
                if not G.has_node(data_receiver):
                    if data_receiver == "":
                        G.add_node(data_receiver, size=40, title="unknown")
                    else:
                        G.add_node(data_receiver, size=40, title=data_receiver)
                if not G.has_edge(data_sender, data_type):
                    G.add_edge(data_sender, data_type, arrows="to")
                if not G.has_edge(data_type, data_receiver):
                    G.add_edge(data_type, data_receiver, group=raw_idx,  description=raw_text, arrows="to")
    return G



def process(input_data, top_n):
    if top_n > 0:
        sorted_results = sorted(input_data.items(), key=lambda x: x[1], reverse=True)
        sorted_results = sorted_results[:top_n]
    else:
        sorted_results = sorted(input_data.items(), key=lambda x: x[1], reverse=False)
        sorted_results = sorted_results[:top_n]
    return sorted_results


def get_network_stats(G, option, top_n):
    if option == 'betweenness':
        output = nx.betweenness_centrality(G)
        return process(output, top_n)
    elif option == 'closeness':
        output = nx.closeness_centrality(G)
        return process(output, top_n)
    elif option == 'centrality':
        output = nx.degree_centrality(G)
        return process(output, top_n)


def get_percentage(input_data, entity_arr):
    count = 0
    tmp_arr = []
    if input_data is not None:
        for item in input_data:
            tmp_arr.append(item[0])
        for item in tmp_arr:
            if item in entity_arr:
                count += 1
        return count / len(input_data)
    else:
        return None


def draw_graph(G, input_file, main_party):
    net = Network(height='500px', width='100%', bgcolor='#ffffff', font_color='#000000')

    # Add nodes
    for node, node_attrs in G.nodes(data=True):
        net.add_node(node, **node_attrs)

    # Add edges
    for source, target in G.edges():
        net.add_edge(source, target)

    net = Network(height="700px", width="100%", cdn_resources="remote", directed=True, notebook=False,
                  select_menu=True, filter_menu=True)
    net.repulsion()
    net.toggle_physics(False)
    net.from_nx(G)
    net.show_buttons(['physics'])

    html_path = input_file.split('_')[0] + '_graph_flow.html'
    # Generate the HTML file
    try:
        net.show(html_path, notebook=False)
        print(f"Network graph has been created and saved as {html_path}")
    except Exception as e:
        print(f"An error occurred while generating the HTML: {e}")
        # Fallback method
        net.save_graph(html_path)
        print(f"Network graph has been saved using the fallback method as {html_path}")

    # Create a new HTML file that includes both the network and the side panel
    interactive_html = 'interaective_network_' + main_party + '.html'
    with open(interactive_html, "w", encoding="utf-8") as f:
        f.write(get_html_template(html_path))

    print("Interactive network saved as 'interactive_network.html'")


def random_sampling(input_data, size):
    data = np.arange(0, len(input_data))
    if len(input_data) >= size:
        samples = np.random.choice(data, size, replace=False)
        output = []
        for idx in samples:
            output.append(input_data[idx])
    else:
        output = input_data
    return output


def save_verification2csv(output_csv, input_data, sampling_rate):
    sampling_size = int(len(input_data) * sampling_rate)
    sample_data = random_sampling(input_data, sampling_size)

    def write_row(row, num_columns):
        if len(row) == num_columns:  # Ensure the row has exactly 6 columns
            writer.writerow(row)
        else:
            print(f"Each row must have exactly {num_columns} columns")

    with open(output_csv, mode='w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write the header (if needed)
        writer.writerow([
                            'Please rate below using the scale (1:Strongly disagree, 2:Disagree, 3:Somewhat disagree, 4:Neither agree nor disagree, 5:Somewhat agree, 6:Agree, 7:Strongly agree.',
                            '', '', '', '', '', ''])
        writer.writerow(['Text_Segment', 'Data_Type', 'Data Type Evaluation (1-7)', 'Data_Category',
                         'Data Category Evaluation (1-7)', 'Sender', 'Data_type', 'Receiver',
                         'Data Flow Evaluation (1-7)', 'Collection party', 'Collection Party Evaluation (1-7)',
                         'Purpose', 'Purpose Evaluation (1-7)', 'Collection method',
                         'Collection Method Evaluation (1-7)'])
        for item in sample_data:
            text_segment = item[0]
            data_type = item[1]
            data_category = item[2]
            sender = item[3]
            receiver = item[4]
            party_category = item[5]
            purpose = item[6]
            collection_method = item[7]
            write_row(
                [text_segment, data_type, ' ', data_category, ' ', sender, data_type, receiver, ' ', party_category,
                 ' ', purpose, ' ', collection_method, ' '], 15)


def save_metrics2csv(input_data, stats_csv):
    with open(stats_csv, mode='w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        for item in input_data:
            writer.writerow([item])


def save_basics2csv(G, data_category_dict, first_party_arr,
                    third_party_arr, user_party_arr, data_output_arr, output_csv):
    number_nodes = nx.number_of_nodes(G)
    number_edges = nx.number_of_edges(G)
    number_first_party = len(first_party_arr)
    number_third_party = len(third_party_arr)
    number_user_party = len(user_party_arr)
    number_data_flows = len(data_output_arr)

    bidirectional_edges = []
    for edge in G.edges():
        u, v = edge
        if G.has_edge(v, u):
            bidirectional_edges.append((u, v))

    # Extract nodes with bidirectional connections
    bidirectional_nodes = set()
    for edge in bidirectional_edges:
        bidirectional_nodes.update(edge)

    print("Bidirectional edges:", bidirectional_edges)
    print("Nodes with bidirectional connections:", list(bidirectional_nodes))

    data_type_keys = list(data_category_dict.keys())

    category_dict = {}

    for key in data_type_keys:
        tmp = data_category_dict[key]
        if tmp not in category_dict:
            category_dict[tmp] = [key]
        else:
            tmp_arr = category_dict[tmp]
            tmp_arr.append(key)
            category_dict[tmp] = tmp_arr

    category_purpose_dict = {}
    for data_output in data_output_arr:
        identified_data_category = data_output[2]
        tmp_purpose = data_output[6]
        purpose_array = tmp_purpose.split(';')

        for identified_data_purpose in purpose_array:
            if identified_data_purpose != '' and identified_data_purpose != ' ':
                if identified_data_category not in category_purpose_dict:
                    purpose_dict = {}
                    purpose_dict[identified_data_purpose] = 1
                    category_purpose_dict[identified_data_category] = purpose_dict
                else:
                    tmp_dict = category_purpose_dict.get(identified_data_category)
                    if identified_data_purpose not in tmp_dict:
                        tmp_dict[identified_data_purpose] = 1
                        category_purpose_dict[identified_data_category] = tmp_dict
                    else:
                        count_purpose = tmp_dict.get(identified_data_purpose)
                        count_purpose += 1
                        tmp_dict[identified_data_purpose] = count_purpose
                        category_purpose_dict[identified_data_category] = tmp_dict



    with open(output_csv, mode='w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(['Number of nodes', number_nodes])
        writer.writerow(['Number of edges', number_edges])
        writer.writerow(['Number of first party entities', number_first_party, *first_party_arr])
        writer.writerow(['Number of third party entities', number_third_party, *third_party_arr])
        writer.writerow(['Number of user party entities', number_user_party, *user_party_arr])
        writer.writerow(['Number of data types', len(data_type_keys)])
        writer.writerow(['Numer of data flows', number_data_flows])

        category_keys = category_dict.keys()
        for key in category_keys:
            values = category_dict.get(key)
            writer.writerow([key, len(values), *values])

        category_keys = category_dict.keys()
        for key in category_keys:
            purpose_dict = category_purpose_dict.get(key)
            if purpose_dict is not None:
                purpose_keys = purpose_dict.keys()
                writer.writerow([key])
                for pkey in purpose_keys:
                    num = purpose_dict.get(pkey)
                    writer.writerow([pkey, num])


def post_processing_simple(input_file, main_party, csv_file, top_n, between_csv, close_csv, central_csv, tree_csv, longest_path_csv, longest_path_length_csv, most_inwards_csv, most_outwards_csv):
    G = get_data_flow_graph_simple(input_file, main_party, csv_file)

    #finding_tree(G)
    # Find and display the longest path
    #longest_path, longest_path_length = longest_path_multidigraph(G)
    #print("Longest path:", longest_path)
    #print("Length of longest path:", longest_path_length)
    #test(data_category_dict, data_output_arr)

    #draw_graph(G, input_file, main_party)

    data_between = get_network_stats(G, 'betweenness', top_n)

    data_close = get_network_stats(G, 'closeness', top_n)

    data_central = get_network_stats(G, 'centrality', top_n)

    save_metrics2csv(data_between, between_csv)
    save_metrics2csv(data_close, close_csv)
    save_metrics2csv(data_central, central_csv)

    tree = finding_tree(G)
    save_metrics2csv(tree, tree_csv)
    # Find and display the longest path
    longest_path, longest_path_length = longest_path_multidigraph(G)

    save_metrics2csv(longest_path, longest_path_csv)






def post_processing(input_file, main_party, csv_file, option, top_n, verification_csv, metrics_csv, basics_csv,
                    sampling_rate=0.4):
    G, data_category_dict, first_party_arr, third_party_arr, user_party_arr, data_flow_completed_arr, data_flow_no_sender_arr, data_flow_no_receiver_arr, data_output_arr = get_data_flow_graph_revised(
        input_file, main_party, csv_file)

    #finding_tree(G)
    # Find and display the longest path
    #longest_path, longest_path_length = longest_path_multidigraph(G)
    #print("Longest path:", longest_path)
    #print("Length of longest path:", longest_path_length)
    #test(data_category_dict, data_output_arr)

    draw_graph(G, input_file, main_party)

    count_u_2_f = 0
    count_u_2_t = 0
    count_f_2_u = 0
    count_f_2_t = 0
    count_f_2_f = 0
    count_t_2_t = 0
    count_t_2_f = 0

    stats_data = []
    # for data_flow in data_output_arr:
    for data_flow in data_flow_completed_arr:
        tmp_arr = data_flow.split('#')
        sender = tmp_arr[0]
        receiver = tmp_arr[2]
        if sender in user_party_arr and receiver in first_party_arr:
            count_u_2_f += 1
            stats_data.append('u_2_f: ' + sender + '-' + tmp_arr[1] + '-' + receiver)
        elif sender in user_party_arr and receiver in third_party_arr:
            count_u_2_t += 1
            stats_data.append('u_2_t: ' + sender + '-' + tmp_arr[1] + '-' + receiver)
        elif sender in first_party_arr and receiver in user_party_arr:
            count_f_2_u += 1
            stats_data.append('f_2_u: ' + sender + '-' + tmp_arr[1] + '-' + receiver)
        elif sender in first_party_arr and receiver in third_party_arr:
            count_f_2_t += 1
            stats_data.append('f_2_t: ' + sender + '-' + tmp_arr[1] + '-' + receiver)
        elif sender in first_party_arr and receiver in first_party_arr:
            count_f_2_f += 1
            stats_data.append('f_2_f: ' + sender + '-' + tmp_arr[1] + '-' + receiver)
        elif sender in third_party_arr and receiver in third_party_arr:
            count_t_2_t += 1
            stats_data.append('t_2_t: ' + sender + '-' + tmp_arr[1] + '-' + receiver)
        elif sender in third_party_arr and receiver in first_party_arr:
            count_t_2_f += 1
            stats_data.append('t_2_f: ' + sender + '-' + tmp_arr[1] + '-' + receiver)


    # stats_data.append(count_u_2_f / len(data_output_arr))
    # stats_data.append(count_u_2_t / len(data_output_arr))
    # stats_data.append(count_f_2_u / len(data_output_arr))
    # stats_data.append(count_f_2_t / len(data_output_arr))
    # stats_data.append(count_f_2_f / len(data_output_arr))
    # stats_data.append(count_t_2_t / len(data_output_arr))
    # stats_data.append(count_t_2_f / len(data_output_arr))

    total_data_flows = len(data_flow_completed_arr)+len(data_flow_no_sender_arr)+len(data_flow_no_receiver_arr)
    stats_data.append(total_data_flows)
    stats_data.append(count_u_2_f / total_data_flows)
    stats_data.append(count_f_2_f / total_data_flows)
    stats_data.append(count_t_2_f / total_data_flows)
    stats_data.append(count_u_2_t / total_data_flows)
    stats_data.append(count_f_2_t / total_data_flows)
    stats_data.append(count_t_2_t / total_data_flows)
    stats_data.append(count_f_2_u / total_data_flows)

    #print("percentage of user to first party is : " + str(count_u_2_f / len(data_output_arr)))
    #print("percentage of user to third party is : " + str(count_u_2_t / len(data_output_arr)))
    #print("percentage of first party to user is : " + str(count_f_2_u / len(data_output_arr)))
    #print("percentage of first party to third party is : " + str(count_f_2_t / len(data_output_arr)))
    #print("percentage of first party to first party is : " + str(count_f_2_f / len(data_output_arr)))
    #print("percentage of third party to third party is : " + str(count_t_2_t / len(data_output_arr)))
    #print("percentage of third party to first party is : " + str(count_t_2_f / len(data_output_arr)))

    # Percentage of uncompleted data flow as an indication of transparency metric
    transparency_score = (len(data_flow_no_receiver_arr) + len(data_flow_no_sender_arr)) / len(data_flow_completed_arr) #TODO: need revise this part
    stats_data.append(transparency_score)
    print("percentage of uncompleted data flow: " + str(transparency_score))
    # Percentage of third parties
    third_party_score = len(third_party_arr) / (len(first_party_arr) + len(user_party_arr) + len(third_party_arr))
    print("percentage of third party entities: " + str(third_party_score))
    stats_data.append(third_party_score)
    data_type_arr = list(data_category_dict.keys())

    # First party entity in top rankings
    score = get_percentage(get_network_stats(G, option, top_n), first_party_arr)
    print('Percentage of first party entities in ' + option + ': ' + str(score))
    stats_data.append(score)
    # Third party entity in top rankings
    score = get_percentage(get_network_stats(G, option, top_n), third_party_arr)
    print('Percentage of third party entities in ' + option + ': ' + str(score))
    stats_data.append(score)
    # Data type in top rankings
    score = get_percentage(get_network_stats(G, option, top_n), data_type_arr)
    print('Percentage of data types in ' + option + ': ' + str(score))
    stats_data.append(score)

    save_metrics2csv(stats_data, metrics_csv)
    save_verification2csv(verification_csv, data_output_arr, sampling_rate)
    save_basics2csv(G, data_category_dict, first_party_arr,
                    third_party_arr, user_party_arr, data_output_arr, basics_csv)



def finding_tree(G):
    G = G.to_undirected()
    trees = []
    for component in nx.connected_components(G):  # For connected components
        subgraph = G.subgraph(component)
        if nx.is_tree(subgraph):
            trees.append(subgraph)
    # Display trees
    print(f"Found {len(trees)} tree(s):")
    for i, tree in enumerate(trees, 1):
        print(f"Tree {i}: Nodes = {list(tree.nodes())}, Edges = {list(tree.edges())}")
    return trees



def longest_path_multidigraph(G):
    G_weighted = nx.Graph()
    for u, v, data in G.edges(data=True):
        if G_weighted.has_edge(u, v):
            G_weighted[u][v]['weight'] += 1
        else:
            G_weighted.add_edge(u, v, weight=1)

    # Detect cycles using a simple algorithm
    try:
        cycles = list(nx.find_cycle(G_weighted, orientation="ignore"))
        print("Cycles detected:", cycles)
        # Remove cycles or handle them
    except nx.NetworkXNoCycle:
        print("No cycles found.")

    DAG = nx.DiGraph()
    for u, v, data in G_weighted.edges(data=True):
        DAG.add_edge(u, v, weight=data['weight'])

    # Ensure DAG
    if not nx.is_directed_acyclic_graph(DAG):
        print("Graph contains cycles; converting to DAG.")
        DAG = nx.DiGraph(nx.minimum_spanning_tree(G_weighted))  # Example heuristic

    # Find the longest path in the DAG
    longest_path = nx.dag_longest_path(DAG, weight='weight')
    longest_path_length = nx.dag_longest_path_length(DAG, weight='weight')
    print("Longest path:", longest_path)
    print("Length of longest path:", longest_path_length)
    return longest_path, longest_path_length
