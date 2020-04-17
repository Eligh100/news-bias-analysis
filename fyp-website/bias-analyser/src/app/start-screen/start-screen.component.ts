import { Component, OnInit, EventEmitter, Output, ViewChild } from '@angular/core';
import { Validators, FormGroup, FormBuilder } from '@angular/forms';
import { AnalysisParametersService } from '../analysis-parameters.service';
import { MatDatepickerInputEvent } from '@angular/material/datepicker';
import { MatInput } from '@angular/material/input';

/**
 * Used for form options
 * viewValue is displayed to user, value is variable used to reference it
 */
export interface FormSelectOption {
  value: string;
  viewValue: string;
}

@Component({
  selector: 'app-start-screen',
  templateUrl: './start-screen.component.html',
  styleUrls: ['./start-screen.component.css']
})
/**
 * Handles form validation for the initial configuration screen
 * Passes submitted data to next stages
 */
export class StartScreenComponent implements OnInit {

  // List of newspapers
  newspapers: FormSelectOption[] = [
    {value: 'bbc', viewValue: "BBC News"},
    {value: 'daily_mail', viewValue: "The Daily Mail"},
    {value: 'guardian', viewValue: "The Guardian"},
    {value: 'independent', viewValue: "The Independent"},
    {value: 'telegraph', viewValue: "The Telegraph"},
    {value: 'mirror', viewValue: "The Daily Mirror"}
  ];

  // List of political parties
  politicalParties: FormSelectOption[] = [
    {value: 'conservative', viewValue: "Conservatives"},
    {value: 'labour', viewValue: "Labour"},
    {value: 'lib_dem', viewValue: "Liberal Democrats"},
    {value: 'snp', viewValue: "Scottish National Party (SNP)"},
    {value: 'green', viewValue: "Green"},
    {value: 'plaid_cymru', viewValue: "Plaid Cymru"},
    {value: 'brexit_party', viewValue: "Brexit Party"},
  ];

  // topics: FormSelectOption[] = [
  //   {value: 'brexit', viewValue: "Brexit/EU"},
  //   {value: 'economy', viewValue: "Economy/Business"},
  //   {value: 'health', viewValue: "Healthcare/NHS"},
  //   {value: 'foreign', viewValue: "Foreign Affairs"},
  //   {value: 'racism', viewValue: "Racism"},
  //   {value: 'environment', viewValue: "Environment/Climate Change"},
  //   {value: 'crime', viewValue: "Law/Police"},
  //   {value: 'schools', viewValue: "Education/Schools"},
  //   {value: 'immigration', viewValue: "Immigration"},
  //   {value: 'scotland', viewValue: "Scotland"},
  //   {value: 'wales', viewValue: "Wales"},
  //   {value: 'ireland', viewValue: "Ireland"},
  // ];

  ////#region  Date variables

  // Used to see when start date has been changed
  @ViewChild('fromInput', {
    read: MatInput
  }) fromInput: MatInput;
  
  // Used to see when end date has been changed
  @ViewChild('toInput', {
    read: MatInput
  }) toInput: MatInput;

  startDate;
  endDate;

  startDateMin: Date = new Date(2019, 7, 22) // Earliest article is 22nd August - nothing to be analysed before this
  startDateMax: Date = new Date();

  endDateMin: Date = new Date(2019, 7, 22) // Earliest article
  endDateMax: Date = new Date();

  ////#endregion

  // Aesthetic
  expansionPanelHeaderText = "";
  introText = "\nT\n";

  // Flags
  isExpanded = true;
  fullsize = true;
  isDisabled = true;

  counter;

  startScreenForm : FormGroup;

  /**
   * 
   * @param fb For the configuration form - to store, validate, and submit the user's choices
   * @param analysisParameters To pass the chosen newspaper and political party to the next section - and allow Amazon API gateway to know
   *                            which items from DynamoDB to collect
   */
  constructor(private fb: FormBuilder, private analysisParameters:AnalysisParametersService) { }

  /**
   * Initialises the form, and flags/counters
   */
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

  /**
   * Changes whether the panel can be opened/closed
   * When the application starts, the user must submit config options
   * After this, they can open and close the panel as they please
   * i.e. if they want to look at what parameters (e.g. start date) they chose, or if they want to change the parameters
   */
  changePanelState(){
    if (this.counter == 0){
      this.counter++;
      this.isDisabled = true;
    } else {
      this.isDisabled = false; // don't want to disable this again - only for the first input
    }
    this.expansionPanelHeaderText = (this.isExpanded) ? "" : "Edit parameters";
  }

  /**
   * Switch a flag
   */
  changePanelSize(){
    this.fullsize = !this.fullsize;
  }

  /**
   * Ran when user presses 'Analyse Bias' button
   * Send selected options to service
   * Allows Amazon API gateway to know which URL to use
   * i.e. which items from DynamoDB to retrieve (e.g. "BBC")
   */
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

  // Gets each form fields value
  get selectedNewspaper() { return this.startScreenForm.get('selectedNewspaper'); }
  get selectedPoliticalParty() { return this.startScreenForm.get('selectedPoliticalParty'); }
  //get selectedTopics() { return this.startScreenForm.get('selectedTopics'); }
  get selectedStartDate() { return this.startScreenForm.get('selectedStartDate'); }
  get selectedEndDate() { return this.startScreenForm.get('selectedEndDate'); }

  /**
   * Set start date to user's chosen value (or null if cleared), and updates bounds accordingly
   * @param event User's chosen start date
   */
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

  /**
   * Set end date to user's chosen value (or null if cleared), and updates bounds accordingly
   * @param event User's chosen end date
   */
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

  /**
   * Reset dates and bounds if form is cleared
   */
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

  /**
   * Ran when user clicks 'Clear' form button
   * Reset all fields to empty, and updates bounds/flags accordingly
   */
  clearForm() {
    this.startScreenForm.reset();

    this.resetDates();

    this.fromInput.value = '';
    this.toInput.value = '';
  }

}
 