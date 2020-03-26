import { Component, OnInit, EventEmitter, Output } from '@angular/core';
import { Validators, FormGroup, FormBuilder } from '@angular/forms';
import { AnalysisParametersService } from '../analysis-parameters.service';
import { MatDatepickerInputEvent } from '@angular/material/datepicker';

export interface FormSelectOption {
  value: string;
  viewValue: string;
}

@Component({
  selector: 'app-start-screen',
  templateUrl: './start-screen.component.html',
  styleUrls: ['./start-screen.component.css']
})
export class StartScreenComponent implements OnInit {

  newspapers: FormSelectOption[] = [
    {value: 'bbc', viewValue: "BBC News"},
    {value: 'daily_mail', viewValue: "The Daily Mail"},
    {value: 'guardian', viewValue: "The Guardian"},
    {value: 'independent', viewValue: "The Independent"},
    {value: 'telegraph', viewValue: "The Telegraph"},
    {value: 'mirror', viewValue: "The Daily Mirror"}
  ];

  politicalParties: FormSelectOption[] = [
    {value: 'conservative', viewValue: "Conservatives"},
    {value: 'labour', viewValue: "Labour"},
    {value: 'lib_dem', viewValue: "Liberal Democrats"},
    {value: 'snp', viewValue: "Scottish National Party (SNP)"},
    {value: 'green', viewValue: "Green"},
    {value: 'plaid_cymru', viewValue: "Plaid Cymru"},
    {value: 'brexit_party', viewValue: "Brexit Party"},
    {value: 'ukip', viewValue: "UKIP"}
  ];

  topics: FormSelectOption[] = [
    {value: 'brexit', viewValue: "Brexit/EU"},
    {value: 'economy', viewValue: "Economy/Business"},
    {value: 'health', viewValue: "Healthcare/NHS"},
    {value: 'foreign', viewValue: "Foreign Affairs"},
    {value: 'racism', viewValue: "Racism"},
    {value: 'environment', viewValue: "Environment/Climate Change"},
    {value: 'crime', viewValue: "Law/Police"},
    {value: 'schools', viewValue: "Education/Schools"},
    {value: 'immigration', viewValue: "Immigration"},
    {value: 'scotland', viewValue: "Scotland"},
    {value: 'wales', viewValue: "Wales"},
    {value: 'ireland', viewValue: "Ireland"},
  ];

  startDate;
  endDate;

  expansionPanelHeaderText = "";
  introText = "\nT\n";
  isExpanded = true;
  fullsize = true;
  isDisabled = true;

  startScreenForm : FormGroup;

  constructor(private fb: FormBuilder, private analysisParameters:AnalysisParametersService) { }

  ngOnInit() {

    this.startScreenForm = this.fb.group({
      selectedNewspaper: ['', [Validators.required]],
      selectedPoliticalParty: ['', [Validators.required]],
      selectedTopics: ['', []],
      selectedStartDate: ['', []],
      selectedEndDate: ['', []],
    })

  }

  changePanelState(){
    this.isDisabled = false; // don't want to disable this again - only for the first input
    this.expansionPanelHeaderText = (this.isExpanded) ? "" : "Edit parameters";
  }

  changePanelSize(){
    this.fullsize = !this.fullsize;
  }

  // send selected options to processing component
  beginAnalysis() {
    this.analysisParameters.analysisParameters = this.startScreenForm;
    this.analysisParameters.startDate = this.startDate;
    this.analysisParameters.endDate = this.endDate
  }

  get selectedNewspaper() { return this.startScreenForm.get('selectedNewspaper'); }
  get selectedPoliticalParty() { return this.startScreenForm.get('selectedPoliticalParty'); }
  get selectedTopics() { return this.startScreenForm.get('selectedTopics'); }
  get selectedStartDate() { return this.startScreenForm.get('selectedStartDate'); }
  get selectedEndDate() { return this.startScreenForm.get('selectedEndDate'); }

  setStartDate(event: MatDatepickerInputEvent<Date>) {
    this.startDate = event.value;
  }

  setEndDate(event: MatDatepickerInputEvent<Date>) {
    this.endDate = event.value;
  }

}
 