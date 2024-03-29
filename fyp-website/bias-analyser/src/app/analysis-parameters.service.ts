import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormGroup } from '@angular/forms';

@Injectable({
  providedIn: 'root'
})
export class AnalysisParametersService {

  analysisParameters: FormGroup

  startDate;
  endDate;

  currentNewspaper = "";

  lastEvaluatedKey: String = "";

  apiURLs = {
    "bbc": "BBC",
    "daily_mail": "DAILY MAIL",
    "guardian": "GUARDIAN",
    "independent": "INDEPENDENT",
    "telegraph": "TELEGRAPH",
    "mirror": "MIRROR",
  }

  constructor(private http:HttpClient) { }

  getPartyInformation() {
    let api_gateway = "https://cev1u7cfnc.execute-api.eu-west-2.amazonaws.com/Party_Production/" + this.analysisParameters.get("selectedPoliticalParty").value
    return this.http.get(api_gateway)
  }

  getArticlesInformation() {
    if (this.lastEvaluatedKey == "") {
      let api_gateway = "https://68m93scoy5.execute-api.eu-west-2.amazonaws.com/Production/" + this.apiURLs[this.analysisParameters.get("selectedNewspaper").value]
      return this.http.get(api_gateway, {responseType: "text"});
    } else {
      let queryString = "?lastEvaluatedKey=" + this.lastEvaluatedKey
      let api_gateway = "https://68m93scoy5.execute-api.eu-west-2.amazonaws.com/Production/" + this.apiURLs[this.analysisParameters.get("selectedNewspaper").value] + queryString
      this.lastEvaluatedKey = "";
      return this.http.get(api_gateway, {responseType: "text"});
    }
    
  }

}