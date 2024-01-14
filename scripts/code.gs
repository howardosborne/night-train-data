function doGet(e) {
  const table = e.parameter.table;
  const sheetId = "15zsK-lBuibUtZ1s2FxVHvAmSu-pEuE0NDT6CAMYL2TY";
  const range = SpreadsheetApp.openById(sheetId).getSheetByName(table).getDataRange().getValues();
  const headers = range[0];
  var rows = {};
  for(var i=1;i<range.length;i++){
      var row = {};
      for(var j=0;j<headers.length;j++){
        row[headers[j]] = range[i][j];
      }
      if(table=="trips"){rows[row[headers[2]]] = row;}
      else{rows[row[headers[0]]] = row;}

  }
  return ContentService.createTextOutput(JSON.stringify(rows)).setMimeType(ContentService.MimeType.JSON);
}
