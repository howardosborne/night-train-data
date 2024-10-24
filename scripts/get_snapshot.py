import requests,json
tables = ["agencies","stops","routes","trips","trip_stop","calendar","calendar_dates","translations","classes","view_ontd_map","view_ontd_list","view_ontd_details"]
for table in tables:
    response = requests.get(f"https://script.google.com/macros/s/AKfycbwY9zNQFq0urCHsTstWRKxLe0SstWrwyY04tSuDIVb_yRCtTs_HDlRARS-5fqltgEZr/exec?table={table}")
    open(f'./data/latest/{table}.json',"w",encoding="UTF-8").write(response.text)
