import { Component, OnInit, EventEmitter, Output, ViewChild } from '@angular/core';
import { Validators, FormGroup, FormBuilder } from '@angular/forms';
import { AnalysisParametersService } from '../analysis-parameters.service';
import { MatDatepickerInputEvent } from '@angular/material/datepicker';
import { MatInput } from '@angular/material/input';

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

  @ViewChild('fromInput', {
    read: MatInput
  }) fromInput: MatInput;
  
  @ViewChild('toInput', {
    read: MatInput
  }) toInput: MatInput;


  startDate;
  endDate;

  startDateMin: Date = new Date(2019, 7, 22) // Earliest article is 22nd August - nothing to be analysed before this
  startDateMax: Date = new Date();

  endDateMin: Date = new Date(2019, 7, 22) // Earliest article
  endDateMax: Date = new Date();

  expansionPanelHeaderText = "";
  introText = "\nT\n";
  isExpanded = true;
  fullsize = true;
  isDisabled = true;

  counter;

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

    this.isDisabled = true;
    
    this.counter = 0;

  }

  changePanelState(){
    if (this.counter == 0){
      this.counter++;
      this.isDisabled = true;
    } else {
      this.isDisabled = false; // don't want to disable this again - only for the first input
    }
    this.expansionPanelHeaderText = (this.isExpanded) ? "" : "Edit parameters";
  }

  changePanelSize(){
    this.fullsize = !this.fullsize;
  }

  // send selected options to processing component
  beginAnalysis() {
    this.analysisParameters.analysisParameters = this.startScreenForm;

    let newspaperViewValue = "";
    for (let i = 0; i < this.newspapers.length; i++) {
      if (this.newspapers[i]["value"] == this.startScreenForm.get('selectedNewspaper').value) {
        newspaperViewValue = this.newspapers[i]["viewValue"];
        break;
      }
    }
  
    this.analysisParameters.currentNewspaper = newspaperViewValue

    this.analysisParameters.startDate = this.startDate;
    this.analysisParameters.endDate = this.endDate
  }

  get selectedNewspaper() { return this.startScreenForm.get('selectedNewspaper'); }
  get selectedPoliticalParty() { return this.startScreenForm.get('selectedPoliticalParty'); }
  get selectedTopics() { return this.startScreenForm.get('selectedTopics'); }
  get selectedStartDate() { return this.startScreenForm.get('selectedStartDate'); }
  get selectedEndDate() { return this.startScreenForm.get('selectedEndDate'); }

  setStartDate(event: MatDatepickerInputEvent<Date>) {
    try {
      this.startDate = event.value;
    } catch {
      this.startDate = null;
    }

    try {
      this.endDateMin = new Date(this.startDate);
    } catch {
      this.endDateMin = new Date(2019, 7, 22);
    }
  }

  setEndDate(event: MatDatepickerInputEvent<Date>) {
    try {
      this.endDate = event.value;
    } catch {
      this.endDate = null;
    }

    try {
      this.startDateMax = new Date(this.endDate); 
    } catch {
      this.startDateMax = new Date();
    }
  }

  resetDates() {
    this.startDate = null;
    this.endDate = null;

    this.startDateMin = new Date(2019, 7, 22);
    this.endDateMin = new Date(2019, 7, 22);

    this.startDateMax = new Date();
    this.endDateMax = new Date();
    
    try {
      this.endDateMin = new Date(this.startDate);
    } catch {
      this.endDateMin = new Date(2019, 7, 22);
    }
  }

  clearForm() {
    this.startScreenForm.reset();

    this.resetDates();

    this.fromInput.value = '';
    this.toInput.value = '';
  }

}
 