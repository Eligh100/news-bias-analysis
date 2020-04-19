import { Component, OnInit, ViewChild, EventEmitter } from '@angular/core';
import { AnalysisParametersService } from '../analysis-parameters.service';
import { CloudData, CloudOptions, TagCloudComponent } from 'angular-tag-cloud-module';
import { Observable, of } from 'rxjs';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { MatSelectChange } from '@angular/material/select';

@Component({
  selector: 'app-bias-analysis-screen',
  templateUrl: './bias-analysis-screen.component.html',
  styleUrls: ['./bias-analysis-screen.component.css']
})
/**
 * Class handles the preparation and displaying of data received from DynamoDB
 * Includes processing charts, calculating bias score, etc.
 */
export class BiasAnalysisScreenComponent implements OnInit {

  //#region CHARTS AND PLOTS

  // Chart types
  public lineChart: string = "line";
  public barChart: string = "bar";
  public doughnutChart: string = "doughnut";
  public radarChart: string = "radar";

  // 'Bias Score' gauge chart
  public canvasWidth = 500
  public needleValue = 100
  public centralLabel = ''
  public bottomLabel = ''
  public options = {
    hasNeedle: true,
    needleColor: 'gray',
    needleUpdateSpeed: 3000,
    arcColors: ['rgb(255, 17, 0)', 'rgb(169, 176, 167)', 'rgb(43,184,0)'],
    arcDelimiters: [33, 67],
    rangeLabel: ['Negative', 'Positive'],
    needleStartValue: 50,
  }
  
  // 'Change in bias over time' line chart
  public biasChangeChartData: Array<any> = [{}];
  public biasChangeChartLabels: Array<any> = [];
  public biasChangeChartColors: Array<any> = [];

  public biasChangeChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Change in party bias over time",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    fill: false,
    scales: {
      xAxes: [{ type: 'time', time: { unit: 'month' }, scaleLabel: { display: true, fontStyle: 'italic', labelString: "Article Publish Date" } }],
      yAxes: [{ id: 'y-axis-1', type: 'linear', position: 'left', ticks: { min: 0, max: 100, callback: function (value) {
        if (value == 100) {
          return value + " (Positive bias)";
        } else if (value == 50) {
          return value + " (Neutral bias)";
        } else if (value == 0) {
          return value + " (Negative bias)";
        } else {
          return value.toFixed(1)
        }
      } }, scaleLabel: { display: true, fontStyle: 'italic', labelString: "Bias Score" } },]
    }
  };

  // 'Topic polarity comparison' bar chart
  public topicPolarityComparisonChartData: Array<any> = [];
  public topicPolarityComparisonChartLabels: Array<any> = [];
  public topicPolarityComparisonChartColors: Array<any> = [];

  public topicPolarityComparisonChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Topics opinions comparison",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    maintainAspectRatio: true,
    scales: {
      xAxes: [{
        ticks: {
          fontSize: 12, callback: function (value) {
            if (value == "Environment/Climate Change") {
              return "Environment/Climate";
            } else {
              return value;
            }
          }
        }, scaleLabel: { display: true, fontStyle: 'italic', labelString: "Topic" }
      }],
      yAxes: [{
        id: 'y-axis-1', type: "linear", position: 'left', ticks: {
          min: -1, max: 1, callback: function (value) {
            if (value == 1) {
              return value + " (Positive opinion)";
            } else if (value == 0) {
              return value + " (Neutral opinion)";
            } else if (value == -1) {
              return value + " (Negative opinion)";
            } else {
              return value.toFixed(1)
            }
          }
        }, scaleLabel: { display: true, fontStyle: 'italic', labelString: "Topic Polarity" }
      },]
    }
  };

  // 'Party polarity comparison' bar chart
  public partyPolarityComparisonChartData: Array<any> = [];
  public partyPolarityComparisonChartLabels: Array<any> = [];
  public partyPolarityComparisonChartColors: Array<any> = [];

  public partyPolarityComparisonChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Party opinions comparison",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    maintainAspectRatio: true,
    scales: {
      xAxes: [{ scaleLabel: { display: true, fontStyle: 'italic', labelString: "Party" } }],
      yAxes: [{
        id: 'y-axis-1', type: "linear", position: 'left', ticks: {
          min: -1, max: 1, callback: function (value) {
            if (value == 1) {
              return value + " (Positive opinion)";
            } else if (value == 0) {
              return value + " (Neutral opinion)";
            } else if (value == -1) {
              return value + " (Negative opinion)";
            } else {
              return value.toFixed(1)
            }
          }
        }, scaleLabel: { display: true, fontStyle: 'italic', labelString: "Party Polarity" }
      },]
    }
  };

  // 'News org change in topic opinion' line chart
  public topicOpinionChangeChartData: Array<any> = [
    { data: [], label: 'Scotland' },
    { data: [], label: 'Ireland' },
    { data: [], label: 'Wales' },
    { data: [], label: 'Brexit/EU' },
    { data: [], label: 'Economy/Business' },
    { data: [], label: 'Healthcare/NHS' },
    { data: [], label: 'Foreign Affairs' },
    { data: [], label: 'Hate Crimes/Discrimination' },
    { data: [], label: 'Environment/Climate Change' },
    { data: [], label: 'Law/Police' },
    { data: [], label: 'Education/Schools' },
    { data: [], label: 'Immigration' }
  ];

  public topicOpinionChangeChartLabels: Array<any> = [];
  public topicOpinionChangeChartColors: Array<any> = [];

  public topicOpinionChangeChartOptions: any = {
    responsive: true,
    spanGaps: true,
    title: {
      display: true,
      text: "Change in topic opinions over time",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    lineTension: 0,
    scales: {
      xAxes: [{ type: 'time', time: { unit: 'month' }, scaleLabel: { display: true, fontStyle: 'italic', labelString: "Article Publish Date" } }],
      yAxes: [{
        id: 'y-axis-1', type: 'linear', position: 'left', ticks: {
          min: -1, max: 1, callback: function (value) {
            if (value == 1) {
              return value + " (Positive opinion)";
            } else if (value == 0) {
              return value + " (Neutral opinion)";
            } else if (value == -1) {
              return value + " (Negative opinion)";
            } else {
              return value.toFixed(1)
            }
          }
        }, scaleLabel: { display: true, fontStyle: 'italic', labelString: "Topic Polarity" }
      },]
    }
  };

  // 'News org change in party opinion' line chart
  public partyOpinionChangeChartData: Array<any> = [
    { data: [], label: 'Labour' },
    { data: [], label: 'Conservatives' },
    { data: [], label: 'Liberal Democrats' },
    { data: [], label: 'Brexit Party' },
    { data: [], label: 'Green' },
    { data: [], label: 'SNP' },
    { data: [], label: 'Plaid Cymru' }
  ];

  public partyOpinionChangeChartLabels: Array<any> = [];
  public partyOpinionChangeChartColors: Array<any> = [];

  public partyOpinionChangeChartOptions: any = {
    responsive: true,
    spanGaps: true,
    title: {
      display: true,
      text: "Change in party opinions over time",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    scales: {
      xAxes: [{ type: 'time', time: { unit: 'month' }, scaleLabel: { display: true, fontStyle: 'italic', labelString: "Article Publish Date" } }],
      yAxes: [{
        id: 'y-axis-1', type: 'linear', position: 'left', ticks: {
          min: -1, max: 1, callback: function (value) {
            if (value == 1) {
              return value + " (Positive opinion)";
            } else if (value == 0) {
              return value + " (Neutral opinion)";
            } else if (value == -1) {
              return value + " (Negative opinion)";
            } else {
              return value.toFixed(1)
            }
          }
        }, scaleLabel: { display: true, fontStyle: 'italic', labelString: "Topic Polarity" }
      },]
    }
  };

  // 'Frequency in topics opinions in articles' bar chart
  public topicPolarityFrequencyChartData: Array<any> = [];
  public topicPolarityFrequencyChartLabels: Array<any> = [];
  public topicPolarityFrequencyChartColors: Array<any> = [];

  public topicPolarityFrequencyChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Topic opinions frequency",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    maintainAspectRatio: true
  };
  
  // 'Frequency in topics in articles' doughnut
  public discussionChartData: Array<any> = [{}];
  public discussionChartLabels: Array<any> = [];
  public discussionChartColors: Array<any> = [];

  public discussionChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Topic discussion frequency in [NEWSPAPER_NAME]",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    }
  };
  
  // 'Frequency in parties in articles' doughnut
  public partyDiscussionChartData: Array<any> = [{}];
  public partyDiscussionChartLabels: Array<any> = [];
  public partyDiscussionChartColors: Array<any> = [];

  public partyDiscussionChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Party discussion frequency in [NEWSPAPER_NAME]",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    }
  };

  // 'Frequency in parties opinions in articles' bar chart
  public partyPolarityFrequencyChartData: Array<any> = [];
  public partyPolarityFrequencyChartLabels: Array<any> = [];
  public partyPolarityFrequencyChartColors: Array<any> = [];

  public partyPolarityFrequencyChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Party opinions frequency",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    maintainAspectRatio: true
  };

  
  // 'Authors topic opinions' bar chart
  public authorTopicPolarityChartData: Array<any> = [];
  public authorTopicPolarityChartLabels: Array<any> = [];
  public authorTopicPolarityChartColors: Array<any> = [];

  public authorTopicPolarityChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Author's topic opinions",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    maintainAspectRatio: true,
    scales: {
      xAxes: [{ scaleLabel: { display: true, fontStyle: 'italic', labelString: "Topic" } }],
      yAxes: [{
        id: 'y-axis-1', type: "linear", position: 'left', ticks: {
          min: -1, max: 1, callback: function (value) {
            if (value == 1) {
              return value + " (Positive opinion)";
            } else if (value == 0) {
              return value + " (Neutral opinion)";
            } else if (value == -1) {
              return value + " (Negative opinion)";
            } else {
              return value.toFixed(1)
            }
          }
        }, scaleLabel: { display: true, fontStyle: 'italic', labelString: "Topic Polarity" }
      },]
    }
  };

  // Author's party opinions' bar chart
  public authorPartyPolarityChartData: Array<any> = [];
  public authorPartyPolarityChartLabels: Array<any> = [];
  public authorPartyPolarityChartColors: Array<any> = [];

  public authorPartyPolarityChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Author's party opinions",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    maintainAspectRatio: true,
    scales: {
      xAxes: [{ scaleLabel: { display: true, fontStyle: 'italic', labelString: "Party" } }],
      yAxes: [{
        id: 'y-axis-1', type: "linear", position: 'left', ticks: {
          min: -1, max: 1, callback: function (value) {
            if (value == 1) {
              return value + " (Positive opinion)";
            } else if (value == 0) {
              return value + " (Neutral opinion)";
            } else if (value == -1) {
              return value + " (Negative opinion)";
            } else {
              return value.toFixed(1)
            }
          }
        }, scaleLabel: { display: true, fontStyle: 'italic', labelString: "Party Polarity" }
      },]
    }
  };

  // Shared language (between articles and manifestos) bar chart
  public sharedLanguageChartData: Array<any> = [];
  public sharedLanguageChartLabels: Array<any> = [];
  public sharedLanguageChartColors: Array<any> = [];

  public sharedLanguageChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Shared language chart",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    maintainAspectRatio: true,
    scales: {
      xAxes: [{ scaleLabel: { display: true, fontStyle: 'italic', labelString: "Party" } }],
      yAxes: [{ scaleLabel: { display: true, fontStyle: 'italic', labelString: "Frequency of articles" }, ticks: { beginAtZero: true } },]

    }
  };

  // Word Cloud Variables
  @ViewChild(TagCloudComponent, { static: false }) wordCloudComponent: TagCloudComponent;

  public cloudOptions: CloudOptions = {
    // if width is between 0 and 1 it will be set to the size of the upper element multiplied by the value 
    width: 1,
    height: 300,
    overflow: false,
  };

  public manifestoWordCloudData: CloudData[] = []; // Word cloud data object of manifestos
  public articlesWordCloudData: CloudData[] = []; // Word cloud data object of articles

  ////#endregion

  // For getting information from DynamoDB table
  public parties_information; // JSON object with 'parties-table' entries
  public articles_information; // JSON object with 'articles-table' entries
  public temp_info;

  ////#region Chart Data Variables

  // Current parties opinion on topics and other parties (for bias score and other charting)
  public partyTopicScores = {};
  public partyToOtherPartiesScores = {};

  // For determining bias score and other charting
  public overallTopicOpinions = {
    "Scotland": [0, 0],
    "Ireland": [0, 0],
    "Wales": [0, 0],
    "Brexit/EU": [0, 0],
    "Economy/Business": [0, 0],
    "Healthcare/NHS": [0, 0],
    "Foreign Affairs": [0, 0],
    "Hate Crimes/Discrimination": [0, 0],
    "Environment/Climate Change": [0, 0],
    "Law/Police": [0, 0],
    "Education/Schools": [0, 0],
    "Immigration": [0, 0]
  }

  // For determining bias score and other charting
  public overallPartyOpinions = {
    "Labour": [0, 0],
    "Conservatives": [0, 0],
    "Liberal Democrats": [0, 0],
    "Brexit Party": [0, 0],
    "Green": [0, 0],
    "SNP": [0, 0],
    "Plaid Cymru": [0, 0]
  }

  // For determining bias score and other charting (shared language chart)
  public similarToPartyText = {
    "Labour": 0,
    "Conservatives": 0,
    "Liberal Democrats": 0,
    "Brexit Party": 0,
    "Green": 0,
    "SNP": 0,
    "Plaid Cymru": 0
  }

  // Opinion polarity frequency variables
  public topicOpinionFrequency = [0, 0, 0] // Index 0 is POSITIVE, 1 is NEUTRAL, 2 is NEGATIVE
  public partyOpinionFrequency = [0, 0, 0] // Index 0 is POSITIVE, 1 is NEUTRAL, 2 is NEGATIVE

  // Date-related variables
  public startDate;
  public endDate;
  public dateToPartyBiasScore = {}; // filled with key: date and values: bias scores - to be plotted
  public dateToTopicScores = {}; // key: date, value: {} of key: topic, value: score
  public dateToPartyScores = {}; // key: date, value: {} of key: party, value: score

  // Topic frequency doughnut variables
  public mostDiscussedArticleTopics = {
    "Scotland": 0,
    "Ireland": 0,
    "Wales": 0,
    "Brexit/EU": 0,
    "Economy/Business": 0,
    "Healthcare/NHS": 0,
    "Foreign Affairs": 0,
    "Hate Crimes/Discrimination": 0,
    "Environment/Climate Change": 0,
    "Law/Police": 0,
    "Education/Schools": 0,
    "Immigration": 0
  }

  // Party frequency doughnut variables
  public mostDiscussedArticleParties = {
    "Labour": 0,
    "Conservatives": 0,
    "Liberal Democrats": 0,
    "Brexit Party": 0,
    "Green": 0,
    "SNP": 0,
    "Plaid Cymru": 0
  }

  // Author variables
  authorsForm: FormGroup;
  public foundAuthors: Array<string> = [];
  public invalidAuthors: Array<string> = ["BBC", "DAILY MAIL", "GUARDIAN", "INDEPENDENT", "TELEGRAPH", "MIRROR"]
  public validAuthors: boolean = false;
  public authorSelected: boolean = false;
  public authorsOpinions = {};

  // Top words from articles and manifestos (for word clouds)
  public newspaperTopWords = {};
  public partyTopWords = {};
  
  ////#endregion

  
  ////#region Aesthetics
  
  public topicColours = {
    "Scotland": ["#FFF700", "#FAF43F"],
    "Ireland": ["#004806", "#1D5622"],
    "Wales": ["#FF0000", "#FF3727"],
    "Brexit/EU": ["#6900FF", "#944DF9"],
    "Economy/Business": ["#d19134", "#d4ab70"],
    "Healthcare/NHS": ["#0D73B7", "#4588b5"],
    "Foreign Affairs": ["#FF00D4", "#FA42DB"],
    "Racism": ["#a37968", "#ebb098"],
    "Environment/Climate Change": ["#2CFF01", "#63FF43"],
    "Law/Police": ["#000A37", "#0F1739"],
    "Education/Schools": ["#70fff1", "#befaf4"],
    "Immigration": ["#ff5500", "#f7996a"]
  };

  public partyColours = {
    "Labour": ["#FF0000", "#FF3727"],
    "Conservatives": ["#0095FF", "#42B1FF"],
    "Liberal Democrats": ["#FF5900", "#F7752F"],
    "Brexit Party": ["#0004ff", "#6669fa"],
    "Green": ["#04ff00", "#77ff75"],
    "SNP": ["#ffe600", "#fced60"],
    "Plaid Cymru": ["#00630c", "#2c6333"]
  };

  // Sentence describing bias score
  public biasSentence;
  public biasSentenceColour;

  // For meta text at bottom, describing how many articles analysed
  public metaInformation: string = "";
  public analysedArticlesCount = 0;

  ////#endregion

  // Stores user's chosen party and paper
  public currentParty;
  public currentNewspaper;

  // Stores bias score - starting from 50 (i.e. neutral)
  // Analysis either adds or subtracts from this, to get final bias score
  public newspaperToPartyBiasScore = 50;

  // The base amount to update the bias score with
  public BASE_BIAS_NUM = 20

  // For aveeraging
  public scoresToAverageCount = 0;

  // Dictates when to show screen to user (once all data has been formatted)
  public processingDone: boolean = false;

  /**
   * 
   * @param fb For choosing authors (need 'select' button)
   * @param _analysisParametersService Allows access to DynamoDB (via Amazon API gateway link)
   */
  constructor(private fb: FormBuilder, private _analysisParametersService: AnalysisParametersService) { }

  /**
   * Initialises variables, and starts process of retrieving article/party information from DynamoDB
   */
  ngOnInit() {
    this.processingDone = false;

    this.authorsForm = this.fb.group({
      selectedAuthor: ['', [Validators.required]],
    });

    this.foundAuthors = [];
    this.validAuthors = false;
    this.authorSelected = false;

    this.needleValue = 50;

    this.articles_information = "";

    this.getDateLimits();
    this.getPartiesInformation();
    this.getArticlesInformation();
  }

  /**
   * Sees if the user has enabled any date ranges
   * This limits the results returned
   */
  getDateLimits() {
    try {
      this.startDate = this._analysisParametersService.startDate._d;
    } catch {
      this.startDate = ""
    }

    try {
      this.endDate = this._analysisParametersService.endDate._d;
    } catch {
      this.endDate = ""
    }
  }

  /**
   * Extract relevant party's JSON object from DynamoDB
   * Containing information relating to the party
   */
  getPartiesInformation() {
    this._analysisParametersService.getPartyInformation().subscribe(
      // the first argument is a function which runs on success
      data => { this.parties_information = data["partiesInfo"][0] },
      // the second argument is a function which runs on error
      err => console.error(err),
      // the third argument is a function which runs on completion
      () => {
        console.log('done loading parties info');
        this.encodePartyInfo()
      }
    );
  }
  
  /**
   * Extract relevant newspapers JSON object from DynamoDB
   * Containing all relevant articles, and their information
   */
  getArticlesInformation() {
    this._analysisParametersService.getArticlesInformation().subscribe(
      // the first argument is a function which runs on success
      data => {
        if (this.articles_information['articleInfo']) {
          this.temp_info = data
        } else {
          this.articles_information = data
        }
      },
      // the second argument is a function which runs on error
      err => console.error(err),
      // the third argument is a function which runs on completion
      () => {
        let lastEvaluatedKey = ""

        // Handles issues with JSON object construction
        // And if returned articles is greater than 1000
        // DynamoDB uses pagination, which limits results to 1000

        if (this.articles_information['articleInfo']) {
          try {
            this.temp_info = JSON.parse(this.temp_info)
          } catch {
            let sliceIndex = this.temp_info.indexOf("\"lastEvaluatedKey\"");

            this.temp_info = this.temp_info.slice(0, (sliceIndex - 13)) + " " + this.temp_info.slice(sliceIndex - 12)
            this.temp_info = JSON.parse(this.temp_info)
          }
          this.articles_information["articleInfo"] = this.articles_information["articleInfo"].concat(this.temp_info["articleInfo"])
          lastEvaluatedKey = this.temp_info["lastEvaluatedKey"]
        } else {

          try {
            this.articles_information = JSON.parse(this.articles_information)
          } catch {
            let sliceIndex = this.articles_information.indexOf("\"lastEvaluatedKey\"");

            this.articles_information = this.articles_information.slice(0, (sliceIndex - 13)) + " " + this.articles_information.slice(sliceIndex - 12)
            this.articles_information = JSON.parse(this.articles_information)
          }

          lastEvaluatedKey = this.articles_information["lastEvaluatedKey"]

        }

        if (lastEvaluatedKey != "") { // If still more results (pagination limits to 1000 per request)
          this._analysisParametersService.lastEvaluatedKey = lastEvaluatedKey;
          this.getArticlesInformation();
        } else { // If all results collected
          this.articles_information = this.articles_information["articleInfo"];
          console.log('done loading articles');
          this.analyseArticleInformation()
        }
      }
    );
  }

  /**
   * Extracts relevant information for chosen political party
   * i.e. topic/other party opinions, and top words from the manifesto
   * Encode into strings for use by charts/data analysis
   */
  encodePartyInfo() {
    let topic_sentiment_matrix_string = this.parties_information["topicsSentimentMatrix"];

    topic_sentiment_matrix_string.split(", ").forEach((topicAndScore) => {
      let split = topicAndScore.split(" = ");
      let topicScore = +(split[1]);
      topicScore = +topicScore.toFixed(2);
      this.partyTopicScores[split[0]] = topicScore;
    });

    let party_sentiment_matrix_string = this.parties_information["partiesSentimentMatrix"];

    party_sentiment_matrix_string.split(", ").forEach((partyAndScore) => {
      let split = partyAndScore.split(" = ");
      let partyScore = +(split[1]);
      partyScore = +partyScore.toFixed(2);
      this.partyToOtherPartiesScores[split[0]] = partyScore;
    });

    this.currentParty = this.parties_information["partyName"]

    this.parties_information["topWords"].split(", ").forEach(element => {
      let split = element.split(" = ");
      let word_freq = +(split[1])
      word_freq = +word_freq.toFixed(2)
      this.partyTopWords[split[0]] = word_freq
    });
  }

  /**
   * Goes through each article retrieved from DynamoDB
   * Calculates bias score for each one, and stores relevant information for plotting
   * Crucial function!
   */
  analyseArticleInformation() {
    this.currentNewspaper = this._analysisParametersService.currentNewspaper;

    // Loops through each found article, from DynamoDB
    this.articles_information.forEach((article) => {

      let articlePubDate = article["articlePubDate"];

      // Decides whether to analyse article - i.e. if article not in chosen date range, ignore it
      if (articlePubDate != "NO INFO" && articlePubDate != "") {
        if (!this.DateRangeCheck(articlePubDate)) {
          return;
        }
      } else {
        if (this.startDate != "" && this.endDate != "") {
          return;
        }
      }

      this.analysedArticlesCount++; // Used to keep track of how many articles have been analysed this run
      this.scoresToAverageCount++; // Used to average total bias score

      let articlePartyBiasScore = 50; // Current article's party bias score - starts at neutral (50)

      // Get the most likely topics, to display what topics the newspaper discusses the most
      let article_topics = (article["articleTopics"]).split(", ")

      article_topics.forEach(element => {
        this.mostDiscussedArticleTopics[element] += 1
      });

      // Get the most likely parties, to display what parties the newspaper discusses the most
      let article_parties = (article["articleParties"]).split(", ")

      article_parties.forEach(element => {
        this.mostDiscussedArticleParties[element] += 1 
      });

      // Get the authors for current article - except for BBC, who don't share author details
      let authors = [];

      if (this.currentNewspaper == "The Telegraph") {
        authors = (article["articleAuthor"]).split("; ");
      } else {
        authors = (article["articleAuthor"]).split(", ");
      }

      let invalidAuthorIndex = -1;
      for (let i = 0; i < this.invalidAuthors.length; i++) {
        invalidAuthorIndex = authors.indexOf(this.invalidAuthors[i])

        if (invalidAuthorIndex != -1)
          break;
      }

      // Remove unknown authors (i.e. just the org name)
      if (invalidAuthorIndex != -1) {
        authors.splice(invalidAuthorIndex, 1);
      }

      authors.forEach(author => {
        if (!this.authorsOpinions[author]) {
          this.authorsOpinions[author] = [{}, {}]; // dict for topics and dict for parties
        }
      });

      // Get headline and article topic sentiments
      // If they align (i.e. positive/negative) with party's view, add to overall bias score
      // Round to 2 d.p
      // If they don't align, subtract from overall bias score
      // Add/subtract score - take 1, and subtract difference (i.e. if party=0.8, and article=0.4, 1 - 0.4 = 0.6 to score)

      let topic_seen = {}; // To fix averages, when same topic seen in both article and headline

      // Gets headline's sentiment about topics (if any)
      let headline_topic_sentiments = article["headlineTopicSentiments"]
      if (headline_topic_sentiments != "NO INFO") {
        headline_topic_sentiments.split(", ").forEach(element => {
          let split = element.split(" = ");
          let topic = split[0]
          let headline_score = +(split[1])
          headline_score = +headline_score.toFixed(2) * 3
          if (headline_score > 1)
            headline_score = 1
          if (headline_score < -1) 
            headline_score = -1
          if (this.partyTopicScores[topic]) { // If the party has an opinion about the topic (from our database)
            if (this.partyTopicScores[topic] < 0 && headline_score < 0 || this.partyTopicScores[topic] > 0 && headline_score > 0) { // if same polarity
              let difference = Math.abs(this.partyTopicScores[topic] - headline_score)
              articlePartyBiasScore += this.BASE_BIAS_NUM - (difference * this.BASE_BIAS_NUM)
            } else if (this.partyTopicScores[topic] > 0 && headline_score < 0 || this.partyTopicScores[topic] < 0 && headline_score > 0) { // if different 
              let difference = Math.abs(this.partyTopicScores[topic] - headline_score)
              articlePartyBiasScore -= (difference / 2) * this.BASE_BIAS_NUM
            } else { // if both zero (i.e. neutral)
              articlePartyBiasScore += this.BASE_BIAS_NUM;
            }
          }
          // To get an average of a newspapers opinions about topics
          this.overallTopicOpinions[topic][0] += headline_score;
          this.overallTopicOpinions[topic][1] += 1;
          topic_seen[topic] = true; // If we see it again in the article, don't add 1 to count (to fix averages)
        });
      }

      let party_seen = {}; // To fix averages, when same party seen in both article and headline

      // Gets headline's sentiment about parties (if any)
      let headline_party_sentiments = article["headlinePartySentiments"];
      if (headline_party_sentiments != "NO INFO") {
        headline_party_sentiments.split(", ").forEach(element => {
          let split = element.split(" = ");
          let party = split[0]
          let headline_score = +(split[1]) * 3
          if (headline_score > 1)
            headline_score = 1
          if (headline_score < -1) 
            headline_score = -1
          headline_score = +headline_score.toFixed(2)
          if (this.partyToOtherPartiesScores[party]) { // If the party has an opinion about another party (from our database)
            if (this.partyToOtherPartiesScores[party] < 0 && headline_score < 0 || this.partyToOtherPartiesScores[party] > 0 && headline_score > 0) { // if same polarity
              let difference = Math.abs(this.partyToOtherPartiesScores[party] - headline_score)
              articlePartyBiasScore += this.BASE_BIAS_NUM - (difference * this.BASE_BIAS_NUM)
            } else if (this.partyToOtherPartiesScores[party] > 0 && headline_score < 0 || this.partyToOtherPartiesScores[party] < 0 && headline_score > 0) { // if different 
              let difference = Math.abs(this.partyToOtherPartiesScores[party] - headline_score)
              articlePartyBiasScore -= (difference / 2) * this.BASE_BIAS_NUM
            } else { // if both zero (i.e. neutral)
              articlePartyBiasScore += this.BASE_BIAS_NUM;
            }
          } else if (party == this.currentParty) { // If the headline has an opinion about the party in question
            articlePartyBiasScore += headline_score * this.BASE_BIAS_NUM
          }
          // To get an average of a newspapers opinions about parties
          this.overallPartyOpinions[party][0] += headline_score;
          this.overallPartyOpinions[party][1] += 1;
          party_seen[party] = true; // If we see it again in the article, don't add 1 to count (to fix averages)
        });
      }

      let topics_to_sentiment = {};

      // Get articles sentiment regarding topics 
      let article_topic_sentiments = article["articleTopicSentiments"]
      if (article_topic_sentiments != "NO INFO") {
        article_topic_sentiments.split(", ").forEach(element => { // TODO consider reworking
          let split = element.split(" = ");
          let topic = split[0]
          let article_score = +(split[1])
          article_score = +article_score.toFixed(2) * 3
          if (article_score > 1)
            article_score = 1
          if (article_score < -1) 
            article_score = -1
          if (this.partyTopicScores[topic]) { // If the party has an opinion about the topic (from our database)
            if (this.partyTopicScores[topic] < 0 && article_score < 0 || this.partyTopicScores[topic] > 0 && article_score > 0) { // if same polarity
              let difference = Math.abs(this.partyTopicScores[topic] - article_score)
              articlePartyBiasScore += this.BASE_BIAS_NUM - (difference * this.BASE_BIAS_NUM)
            } else if (this.partyTopicScores[topic] > 0 && article_score <= 0 || this.partyTopicScores[topic] <= 0 && article_score > 0) { // if different 
              let difference = Math.abs(this.partyTopicScores[topic] - article_score)
              articlePartyBiasScore -= (difference / 2) * this.BASE_BIAS_NUM
            } // else { // if both zero (i.e. neutral)
            //   articlePartyBiasScore += this.BASE_BIAS_NUM; // TODO check
            // }
          }
          // To get an average of a newspapers opinions about topics
          this.overallTopicOpinions[topic][0] += article_score;
          if (!topic_seen[topic])
            this.overallTopicOpinions[topic][1] += 1;

          // To get an average of an authors opinions about topics
          authors.forEach(author => {
            if (this.foundAuthors.indexOf(author) == -1) {
              this.foundAuthors.push(author);
              if (!this.validAuthors)
                this.validAuthors = true;
            }

            if (!this.authorsOpinions[author][0][topic]) {
              this.authorsOpinions[author][0][topic] = [0, 0];
            }
            this.authorsOpinions[author][0][topic][0] += article_score;
            this.authorsOpinions[author][0][topic][1] += 1;
          });

          // To track topic opinion changes over time 
          topics_to_sentiment[topic] = article_score;
        });
      }

      let parties_to_sentiment = {};

      // Get articles sentiment regarding political parties
      let article_party_sentiments = article["articlePartySentiments"]
      if (article_party_sentiments != "NO INFO") {
        article_party_sentiments.split(", ").forEach(element => {
          let split = element.split(" = ");
          let party = split[0]
          let article_score = +(split[1])
          article_score = +article_score.toFixed(2) * 3
          if (article_score > 1)
            article_score = 1
          if (article_score < -1) 
            article_score = -1
          if (this.partyToOtherPartiesScores[party]) { // If the party has an opinion about another party (from our database)
            if (this.partyToOtherPartiesScores[party] < 0 && article_score < 0 || this.partyToOtherPartiesScores[party] > 0 && article_score > 0) { // if same polarity
              let difference = Math.abs(this.partyToOtherPartiesScores[party] - article_score)
              articlePartyBiasScore += this.BASE_BIAS_NUM - (difference * this.BASE_BIAS_NUM)
            } else if (this.partyToOtherPartiesScores[party] > 0 && article_score <= 0 || this.partyToOtherPartiesScores[party] <= 0 && article_score > 0) { // if different 
              let difference = Math.abs(this.partyToOtherPartiesScores[party] - article_score)
              articlePartyBiasScore -= (difference / 2) * this.BASE_BIAS_NUM
            }
            // } else { // if both zero (i.e. neutral)
            //   articlePartyBiasScore += this.BASE_BIAS_NUM;
            // }
          } else if (party == this.currentParty) { // If the article has an opinion about the party in question
            articlePartyBiasScore += article_score * this.BASE_BIAS_NUM * 2;
          }
          // To get an average of a newspapers opinions about parties
          this.overallPartyOpinions[party][0] += article_score;
          if (!party_seen[party])
            this.overallPartyOpinions[party][1] += 1;

          // To get an average of an authors opinions about parties
          authors.forEach(author => {
            if (this.foundAuthors.indexOf(author) == -1) {
              this.foundAuthors.push(author);
              if (!this.validAuthors)
                this.validAuthors = true;
            }

            if (!this.authorsOpinions[author][1][party]) {
              this.authorsOpinions[author][1][party] = [0, 0];
            }
            this.authorsOpinions[author][1][party][0] += article_score;
            this.authorsOpinions[author][1][party][1] += 1;
          });

          // To track party opinion changes over time
          parties_to_sentiment[party] = article_score;
        });
      }

      // Get most likely party, and store
      let mostLikelyParty = article["mostLikelyParty"]
      this.similarToPartyText[mostLikelyParty] += 1;

      // If the article is most similar to the current parties manifesto, add to bias score
      if (mostLikelyParty == this.currentParty) {
        if (mostLikelyParty == "Conservatives") {
          articlePartyBiasScore += (this.BASE_BIAS_NUM / 20);
        } else if (mostLikelyParty == "Labour") {
          articlePartyBiasScore += (this.BASE_BIAS_NUM / 18);
        } else {
          articlePartyBiasScore += this.BASE_BIAS_NUM;
        }
      } else {
        // If article is using language similar to the Labour manifesto
        // And we are evaluating the Conservative Party
        // Since the Conservative Party has a negative opinion on the Labour party, we can say
        // That the article is biased AGAINST the Conservative party
        // Add or subtract, weighted by the current party's opinion about the article's most similar party
        if (this.partyToOtherPartiesScores[mostLikelyParty]) {
          if (mostLikelyParty == "Conservatives") {
            articlePartyBiasScore += (this.partyToOtherPartiesScores[mostLikelyParty] * this.BASE_BIAS_NUM) / 20
          } else if (mostLikelyParty == "Labour") {
            articlePartyBiasScore += (this.partyToOtherPartiesScores[mostLikelyParty] * this.BASE_BIAS_NUM) / 18
          } else {
            articlePartyBiasScore += this.partyToOtherPartiesScores[mostLikelyParty] * this.BASE_BIAS_NUM
          }
        }
      }

      // Get the top words, and store in dict - if exists, update with frequency
      if (article["topWords"] != "NO INFO") {
        article["topWords"].split(", ").forEach(element => {
          let split = element.split(" = ");
          let word = split[0]
          let word_freq = +(split[1])
          word_freq = +word_freq.toFixed(2)
          if (this.newspaperTopWords[word]) { // if exists, add to score
            this.newspaperTopWords[word] += word_freq;
          } else { // otherwise, make new entry
            this.newspaperTopWords[word] = word_freq;
          }
        });
      }

      articlePartyBiasScore = +articlePartyBiasScore.toFixed(1);

      // Bound bias score
      if (articlePartyBiasScore < 0) {
        articlePartyBiasScore = 0;
      } else if (articlePartyBiasScore > 100) {
        articlePartyBiasScore = 100;
      }

      // Add to cumulative bias score, to be averaged (for final score)
      if (articlePartyBiasScore < 44 || articlePartyBiasScore > 56) {
        if (articlePartyBiasScore >= 57 && articlePartyBiasScore <= 70) {
          articlePartyBiasScore += 20
          this.newspaperToPartyBiasScore += articlePartyBiasScore
        } else if (articlePartyBiasScore >= 30 && articlePartyBiasScore <= 43) {
          articlePartyBiasScore -= 20
          this.newspaperToPartyBiasScore += articlePartyBiasScore 
        } else {
          this.newspaperToPartyBiasScore += articlePartyBiasScore;
        }
      } else {
        this.scoresToAverageCount--;
      }

      // Handles storing of topic/party opinions for current date
      // Allows plotting changes over time
      if (articlePubDate != "NO INFO" && articlePubDate != "") {
        if (!this.dateToPartyBiasScore[articlePubDate]) {
          this.dateToPartyBiasScore[articlePubDate] = []
        }
        this.dateToPartyBiasScore[articlePubDate].push(articlePartyBiasScore)

        if (!this.dateToTopicScores[articlePubDate]) {
          this.dateToTopicScores[articlePubDate] = {}
        }

        for (let key in topics_to_sentiment) {
          if (!this.dateToTopicScores[articlePubDate][key]) {
            this.dateToTopicScores[articlePubDate][key] = [];
          }
          this.dateToTopicScores[articlePubDate][key].push(topics_to_sentiment[key])

          if (topics_to_sentiment[key] > 0.33) {
            this.topicOpinionFrequency[0]++;
          } else if (topics_to_sentiment[key] < -0.33) {
            this.topicOpinionFrequency[2]++;
          } else {
            this.topicOpinionFrequency[1]++;
          }
        }

        if (!this.dateToPartyScores[articlePubDate]) {
          this.dateToPartyScores[articlePubDate] = {}
        }

        for (let key in parties_to_sentiment) {
          if (!this.dateToPartyScores[articlePubDate][key]) {
            this.dateToPartyScores[articlePubDate][key] = [];
          }
          this.dateToPartyScores[articlePubDate][key].push(parties_to_sentiment[key])

          if (parties_to_sentiment[key] > 0.33) {
            this.partyOpinionFrequency[0]++;
          } else if (parties_to_sentiment[key] < -0.33) {
            this.partyOpinionFrequency[2]++;
          } else {
            this.partyOpinionFrequency[1]++;
          }
        }
      }
    })

    // Once all articles analysed, get average overall score
    let finalBiasValue = this.newspaperToPartyBiasScore / this.scoresToAverageCount

    console.log(finalBiasValue)

    // Bound final score
    if (finalBiasValue < 0) {
      finalBiasValue = 0;
    } else if (finalBiasValue > 100) {
      finalBiasValue = 100;
    }

    // Set needle value of gauge chart
    this.needleValue = finalBiasValue

    // Label gauge chart accordingly
    if (this.needleValue <= 33) {
      if (this.needleValue <= 16) {
        this.biasSentence = "HIGH NEGATIVE bias"
        this.biasSentenceColour = "#8f0000"
      } else {
        this.biasSentence = "a NEGATIVE bias"
        this.biasSentenceColour = "#ff0000"
      }
    } else if (this.needleValue >= 67) {
      if (this.needleValue >= 83) {
        this.biasSentence = "HIGH POSITIVE bias"
        this.biasSentenceColour = "#00630c"
      } else {
        this.biasSentence = "a POSITIVE bias"
        this.biasSentenceColour = "#1eff00"
      }
    } else {
      if (this.needleValue < 44) {
        this.biasSentence = "a slight NEGATIVE bias"
        this.biasSentenceColour = "#ff7070"
      } else if (this.needleValue > 56) {
        this.biasSentence = "a slight POSITIVE bias"
        this.biasSentenceColour = "#57c960"
      } else {
        this.biasSentence = "NO BIAS"
        this.biasSentenceColour = "#828282"
      }
    }

    // Sort the authors for easy searching/selection in select box
    this.foundAuthors.sort();

    // Plot the various graphs, charts, and plots
    this.plotBiasChangeGraph();

    this.plotTopicOpinionComparisonGraph();
    this.plotPartyOpinionComparisonGraph();

    this.plotTopicChangeGraph();
    this.plotPartyChangeGraph();

    this.constructDiscussedTopicsDoughnut();
    this.plotTopicOpinionFrequencyGraph();

    this.constructDiscussedPartiesDoughnut();
    this.plotPartyOpinionFrequencyGraph();

    this.plotSharedLanguageGraph();

     // Finally, show the results
    this.processingDone = true;

    // Construct word clouds after showing, due to screen-drawing issues
    this.constructManifestoWordCloud();
    this.constructArticlesWordCloud();

  }

  /**
   * Plots newspaper's change in bias (against chosen political party) over time
   * Each article has a bias score, this is plotted
   */
  plotBiasChangeGraph() {
    let data = [];
    let label = this.currentNewspaper + this.GrammarChecker(this.currentNewspaper) + " bias score towards " + this.currentParty;

    let tempChartData = []
    let tempChartLabels = []

    let sortedDatesAndScore = [];

    for (let key in this.dateToPartyBiasScore) {

      let scores = this.dateToPartyBiasScore[key];

      let total = 0;

      for (let i = 0; i < scores.length; i++) {
        total += scores[i];
      }

      let average = total / scores.length

      sortedDatesAndScore.push([key, average])
    }

    sortedDatesAndScore = sortedDatesAndScore.sort(this.DateComparator);

    this.setMetaInfo(sortedDatesAndScore[0][0], sortedDatesAndScore[sortedDatesAndScore.length - 1][0]);

    for (let i = 0; i < sortedDatesAndScore.length; i++) {
      tempChartLabels.push(sortedDatesAndScore[i][0]);
      data.push(sortedDatesAndScore[i][1].toFixed(3));
    }

    tempChartData.push({ data: data, label: label, fill: false, backgroundColor: this.partyColours[this.currentParty][1], borderColor: this.partyColours[this.currentParty][0], pointRadius: 2, pointBorderColor: "black" });

    this.biasChangeChartData = tempChartData;
    this.biasChangeChartLabels = tempChartLabels;
    this.biasChangeChartColors = this.partyColours[this.currentParty][0];

    this.biasChangeChartOptions["title"]["text"] = this.currentNewspaper + this.GrammarChecker(this.currentNewspaper) + " change in bias towards " + this.currentParty;

  }

  /**
   * Gets average topic opinion from across all articles
   * Compares to topic opinions from party (extracted from manifesto, stored in DynamoDB)
   */
  plotTopicOpinionComparisonGraph() {
    let tempData = [];
    let labels = [];
    let colours = ["#8c8c8c", this.partyColours[this.currentParty][0]];

    let newspaperData = [];
    let newspaperLabel = this.currentNewspaper + this.GrammarChecker(this.currentNewspaper) + " opinion on topics";

    let partyData = [];
    let partyLabel = this.currentParty + this.GrammarChecker(this.currentNewspaper) + " opinion on topics";

    for (let key in this.topicColours) {
      let value;

      // First, get newspaper's average polarity on topic
      if (this.overallTopicOpinions[key]) {
        if (this.overallTopicOpinions[key][1] != 0) {
          value = this.overallTopicOpinions[key][0];
          value = (value / this.overallTopicOpinions[key][1]).toFixed(3); // Get average polarity score for topic
        } else {
          value = 0;
        }
      } else {
        value = 0;
      }

      if (value > 1) {
        value = 1;
      } else if (value < -1) {
        value = -1;
      }

      newspaperData.push(value);

      // Then, get party's polarity on topic
      if (this.partyTopicScores[key]) {
        value = this.partyTopicScores[key]
      } else {
        value = 0;
      }

      partyData.push(value);

      // Add the topic for our X-axis
      labels.push(key);
    }

    tempData.push({ data: newspaperData, label: newspaperLabel, backgroundColor: "#8c8c8c", borderColor: "#696969" });
    tempData.push({ data: partyData, label: partyLabel, backgroundColor: this.partyColours[this.currentParty][1], borderColor: this.partyColours[this.currentParty][0] });

    this.topicPolarityComparisonChartData = tempData;
    this.topicPolarityComparisonChartLabels = labels;
    this.topicPolarityComparisonChartColors = colours;
    this.topicPolarityComparisonChartOptions["title"]["text"] = this.currentNewspaper + " and " + this.currentParty + this.GrammarChecker(this.currentParty) + " opinions about topics";

  }

  /**
   * Gets average party opinion from across all articles
   * Compares to party opinions from party (extracted from manifesto, stored in DynamoDB) - and not including itself
   */
  plotPartyOpinionComparisonGraph() {
    let tempData = [];
    let labels = [];
    let colours = ["#8c8c8c"];

    let newspaperData = [];
    let newspaperLabel = this.currentNewspaper + this.GrammarChecker(this.currentNewspaper) + " opinion on other parties";

    let partyData = [];
    let partyLabel = this.currentParty + this.GrammarChecker(this.currentParty) + " opinion on other parties";

    for (let key in this.partyColours) {
      if (key != this.currentParty) {

        let value;

        // First, get newspaper's average polarity on topic
        if (this.overallPartyOpinions[key]) {
          if (this.overallPartyOpinions[key][1] != 0) {
            value = this.overallPartyOpinions[key][0];
            value = (value / this.overallPartyOpinions[key][1]).toFixed(3); // Get average polarity score for party
          } else {
            value = 0;
          }
        } else {
          value = 0;
        }

        if (value > 1) {
          value = 1;
        } else if (value < -1) {
          value = -1;
        }

        newspaperData.push(value);

        // Then, get party's polarity on topic
        if (this.partyToOtherPartiesScores[key]) {
          value = this.partyToOtherPartiesScores[key]
        } else {
          value = 0;
        }

        partyData.push(value);

        // Add the topic for our X-axis
        labels.push(key);
      }
    }

    tempData.push({ data: newspaperData, label: newspaperLabel, backgroundColor: "#8c8c8c", borderColor: "#696969" });
    tempData.push({ data: partyData, label: partyLabel, backgroundColor: this.partyColours[this.currentParty][1], borderColor: this.partyColours[this.currentParty][0] });

    this.partyPolarityComparisonChartData = tempData;
    this.partyPolarityComparisonChartLabels = labels;
    this.partyPolarityComparisonChartColors = colours;
    this.partyPolarityComparisonChartOptions["title"]["text"] = this.currentNewspaper + " and " + this.currentParty + this.GrammarChecker(this.currentParty) + " opinions about other parties";

  }

  /**
   * Each article has opinions about topics
   * Plots change in opinions about each topic over time
   * Some topics are discussed more, so more data for the chart
   */
  plotTopicChangeGraph() {

    let tempChartData = this.topicOpinionChangeChartData;
    let tempChartLabels = [];
    let tempColours = []

    let sortedDatesAndTopicScoreDict = [];

    for (let date in this.dateToTopicScores) {

      let topicScoreDict = this.dateToTopicScores[date];

      sortedDatesAndTopicScoreDict.push([date, topicScoreDict]);
    }

    sortedDatesAndTopicScoreDict = sortedDatesAndTopicScoreDict.sort(this.DateComparator);

    for (let i = 0; i < sortedDatesAndTopicScoreDict.length; i++) {
      let date = sortedDatesAndTopicScoreDict[i][0];
      let topicScoreDict = sortedDatesAndTopicScoreDict[i][1];

      tempChartLabels.push(date)

      let counter = 0
      for (let topic in this.topicColours) {
        if (topicScoreDict[topic]) { // if any articles from this date DO mention x topic
          let scores = topicScoreDict[topic];
          let total = 0;
          for (let i = 0; i < scores.length; i++) {
            let score = scores[i]
            if (score < -1) {
              score = -1
            } else if (score > 1) {
              score = 1
            }
            total += score;
          }
          let average = total / scores.length

          tempChartData[counter]["data"].push({ "x": date, "y": average.toFixed(3) })
        } else { // if any articles from this date DON'T mention x topic
          tempChartData[counter]["data"].push(null)
        }

        tempChartData[counter]["fill"] = false;
        tempChartData[counter]["pointRadius"] = 2;
        tempChartData[counter]["pointBorderColor"] = "black";

        if (counter != 0) {
          tempChartData[counter]["hidden"] = true;
        }

        tempColours.push({ backgroundColor: this.topicColours[topic][1], borderColor: this.topicColours[topic][0] });

        counter++;
      }
    }

    this.topicOpinionChangeChartData = tempChartData;
    this.topicOpinionChangeChartLabels = tempChartLabels;
    this.topicOpinionChangeChartColors = tempColours;
    this.topicOpinionChangeChartOptions["title"]["text"] = this.currentNewspaper + this.GrammarChecker(this.currentNewspaper) + " change in topic opinions over time";

  }

  /**
   * Each article has opinions about parties
   * Plots change in opinions about each party over time
   * Some parties are discussed more, so more data for the chart
   */
  plotPartyChangeGraph() {
    let data = [];
    let label = "[Newspaper] party opinions change over time";

    let tempChartData = this.partyOpinionChangeChartData;
    let tempChartLabels = []
    let tempColours = []

    let sortedDatesAndPartyScoreDict = [];

    for (let date in this.dateToPartyScores) {

      let dateScoreDict = this.dateToPartyScores[date];

      sortedDatesAndPartyScoreDict.push([date, dateScoreDict]);
    }

    sortedDatesAndPartyScoreDict = sortedDatesAndPartyScoreDict.sort(this.DateComparator);

    for (let i = 0; i < sortedDatesAndPartyScoreDict.length; i++) {
      let date = sortedDatesAndPartyScoreDict[i][0];
      let partyScoreDict = sortedDatesAndPartyScoreDict[i][1];

      tempChartLabels.push(date)

      let counter = 0
      for (let party in this.partyColours) {
        if (partyScoreDict[party]) { // if any articles from this date DO mention x topic

          let scores = partyScoreDict[party];
          let total = 0;
          for (let i = 0; i < scores.length; i++) {
            let score = scores[i]
            if (score < -1) {
              score = -1
            } else if (score > 1) {
              score = 1
            }
            total += score;
          }
          let average = total / scores.length

          tempChartData[counter]["data"].push({ "x": date, "y": average.toFixed(3) })
        } else { // if any articles from this date DON'T mention x topic
          tempChartData[counter]["data"].push(null)
        }

        tempChartData[counter]["fill"] = false;
        tempChartData[counter]["pointRadius"] = 2;
        tempChartData[counter]["pointBorderColor"] = "black";

        if (counter != 0) {
          tempChartData[counter]["hidden"] = true;
        }

        tempColours.push({ backgroundColor: this.partyColours[party][1], borderColor: this.partyColours[party][0] });

        counter++;
      }
    }

    this.partyOpinionChangeChartData = tempChartData;
    this.partyOpinionChangeChartLabels = tempChartLabels;
    this.partyOpinionChangeChartColors = tempColours;
    this.partyOpinionChangeChartOptions["title"]["text"] = this.currentNewspaper + this.GrammarChecker(this.currentNewspaper) + " change in party opinions over time";

  }

  /**
   * Each article has opinions about topics
   * Charts frequency of mentioned topics
   * Allows user to see how much a topic is mentioned over other topics
   */
  constructDiscussedTopicsDoughnut() {
    let tempDoughnutData = [];
    let doughnutData = [];

    let doughnutLabels = [];

    let tempColours = [];
    let doughnutMainColours = [];
    let doughnutHoverColours = [];

    for (let key in this.mostDiscussedArticleTopics) {
      if (key != "NO INFO" && key != "undefined") {
        doughnutLabels.push(key);

        let value = this.mostDiscussedArticleTopics[key];
        doughnutData.push(value);

        try {
          doughnutMainColours.push(this.topicColours[key][0])
          doughnutHoverColours.push(this.topicColours[key][1])
        }
        catch {
          doughnutLabels.pop();
          doughnutData.pop();
          continue;
        }
      }
    }

    tempDoughnutData.push({ data: doughnutData, label: "Topic discussion frequency over all articles" })

    tempColours.push(
      {
        backgroundColor: doughnutMainColours,
        hoverBackgroundColor: doughnutHoverColours,
        borderWidth: 2,
      }
    )

    this.discussionChartData = tempDoughnutData;
    this.discussionChartLabels = doughnutLabels;
    this.discussionChartColors = tempColours;
    this.discussionChartOptions["title"]["text"] = this.currentNewspaper + this.GrammarChecker(this.currentNewspaper) + " distribution of discussed topics";

  }

  /**
   * Each article has opinions about topics
   * Charts frequency of different polarities of opinions
   * Can see how many positive views on topics a newspaper has, compared to neutral and negative
   */
  plotTopicOpinionFrequencyGraph() {
    let tempData = [];
    let labels = ["Positive", "Neutral", "Negative"];
    let colours = ["#0ba600", "#a1a1a1", "#ff0d00"];

    let data = [];

    for (let i = 0; i < this.topicOpinionFrequency.length; i++) {
      data.push(this.topicOpinionFrequency[i]);
    }

    tempData.push({ data: data, label: "Frequency of opinion", backgroundColor: colours });

    this.topicPolarityFrequencyChartData = tempData;
    this.topicPolarityFrequencyChartLabels = labels;
    this.topicPolarityFrequencyChartColors = colours;

    this.topicPolarityFrequencyChartOptions["title"]["text"] = this.currentNewspaper + this.GrammarChecker(this.currentNewspaper) + " distribution of topic opinions";
    console.log(this.topicOpinionChangeChartOptions)

  }

  /**
   * Each article has opinions about parties
   * Charts frequency of mentioned parties
   * Allows user to see how much a party is mentioned over other parties
   */
  constructDiscussedPartiesDoughnut() {
    let tempDoughnutData = [];
    let doughnutData = [];

    let doughnutLabels = [];

    let tempColours = [];
    let doughnutMainColours = [];
    let doughnutHoverColours = [];

    for (let key in this.mostDiscussedArticleParties) {
      if (key != "NO INFO" && key != "undefined") {
        doughnutLabels.push(key);

        let value = this.mostDiscussedArticleParties[key];
        doughnutData.push(value);

        try {
          doughnutMainColours.push(this.partyColours[key][0])
          doughnutHoverColours.push(this.partyColours[key][1])
        }
        catch {
          doughnutLabels.pop();
          doughnutData.pop();
          continue;
        }
      }
    }

    tempDoughnutData.push({ data: doughnutData, label: "Party discussion frequency over all articles" })

    tempColours.push(
      {
        backgroundColor: doughnutMainColours,
        hoverBackgroundColor: doughnutHoverColours,
        borderWidth: 2,
      }
    )

    this.partyDiscussionChartData = tempDoughnutData;
    this.partyDiscussionChartLabels = doughnutLabels;
    this.partyDiscussionChartColors = tempColours;
    this.partyDiscussionChartOptions["title"]["text"] = this.currentNewspaper + this.GrammarChecker(this.currentNewspaper) + " distribution of discussed parties";

  }

  /**
   * Each article has opinions about parties
   * Charts frequency of different polarities of opinions
   * Can see how many positive views on parties a newspaper has, compared to neutral and negative
   */
  plotPartyOpinionFrequencyGraph() {
    let tempData = [];
    let labels = ["Positive", "Neutral", "Negative"];
    let colours = ["#0ba600", "#a1a1a1", "#ff0d00"];

    let data = [];

    for (let i = 0; i < this.partyOpinionFrequency.length; i++) {
      data.push(this.partyOpinionFrequency[i]);
    }

    tempData.push({ data: data, label: "Frequency of opinion", backgroundColor: colours });

    this.partyPolarityFrequencyChartData = tempData;
    this.partyPolarityFrequencyChartLabels = labels;
    this.partyPolarityFrequencyChartColors = colours;

    this.partyPolarityFrequencyChartOptions["title"]["text"] = this.currentNewspaper + this.GrammarChecker(this.currentNewspaper) + " distribution of party opinions";

  }

  /**
   * Each article has opinions about topics
   * And each article has an author
   * Charts average topic opinions for an author
   */  
  plotAuthorTopicOpinionGraph(author: string) {
    let tempData = [];
    let labels = [];
    let colours = [];

    let authorData = [];
    let authorLabel = author + this.GrammarChecker(author) + " opinion on topics";


    for (let key in this.topicColours) {
      let value;

      // First, get author's average polarity on topic
      if (this.authorsOpinions[author][0][key]) {
        if (this.authorsOpinions[author][0][key][1] != 0) {
          value = this.authorsOpinions[author][0][key][0];
          value = (value / this.authorsOpinions[author][0][key][1]).toFixed(3); // Get average polarity score for topic
        } else {
          value = 0;
        }

        // Add the topic for our X-axis
        labels.push(key);

        if (value > 1) {
          value = 1;
        } else if (value < -1) {
          value = -1;
        }

        if (value >= 0.33) {
          colours.push("#0ba600");
        } else if (value <= -0.33) {
          colours.push("#ff0d00");
        } else {
          colours.push("#a1a1a1");
        }

        authorData.push(value);
      }

    }

    tempData.push({ data: authorData, label: authorLabel, backgroundColor: colours });

    this.authorTopicPolarityChartData = tempData;
    this.authorTopicPolarityChartLabels = labels;
    this.authorTopicPolarityChartColors = colours;
    this.authorTopicPolarityChartOptions["title"]["text"] = author + this.GrammarChecker(author) + " opinions about topics";

  }

  /**
   * Each article has opinions about parties
   * And each article has an author
   * Charts average party opinions for an author
   */  
  plotAuthorPartyOpinionGraph(author: string) {
    let tempData = [];
    let labels = [];
    let colours = [];

    let authorData = [];
    let authorLabel = author + this.GrammarChecker(author) + " opinion on parties";


    for (let key in this.partyColours) {
      let value;

      // First, get author's average polarity on party
      if (this.authorsOpinions[author][1][key]) {
        if (this.authorsOpinions[author][1][key][1] != 0) {
          value = this.authorsOpinions[author][1][key][0];
          value = (value / this.authorsOpinions[author][1][key][1]).toFixed(3); // Get average polarity score for topic
        } else {
          value = 0;
        }

        // Add the party for our X-axis
        labels.push(key);

        if (value > 1) {
          value = 1;
        } else if (value < -1) {
          value = -1;
        }

        if (value >= 0.33) {
          colours.push("#0ba600");
        } else if (value <= -0.33) {
          colours.push("#ff0d00");
        } else {
          colours.push("#a1a1a1");
        }

        authorData.push(value);
      }

    }

    tempData.push({ data: authorData, label: authorLabel, backgroundColor: colours });

    this.authorPartyPolarityChartData = tempData;
    this.authorPartyPolarityChartLabels = labels;
    this.authorPartyPolarityChartColors = colours;
    this.authorPartyPolarityChartOptions["title"]["text"] = author + this.GrammarChecker(author) + " opinions about parties";

  }

  /**
   * Each article is compared (via TF-IDF/cosine similarity) to the manifestos
   * This chart plots the frequency of articles deemed 'most-similar' to each manifesto
   * Allows user to get idea of how language carries over between news and manifestos
   */  
  plotSharedLanguageGraph() {
    let tempData = [];
    let labels = [];
    let colours = [];
    let borders = [];

    let data = [];

    for (let key in this.partyColours) {
      labels.push(key)
      colours.push(this.partyColours[key][1])
      borders.push(this.partyColours[key][0])
      data.push(this.similarToPartyText[key])
    }

    tempData.push({ data: data, label: "No. of articles using language similar to party manifesto", backgroundColor: colours, borderColor: borders });

    this.sharedLanguageChartData = tempData;
    this.sharedLanguageChartLabels = labels;
    this.sharedLanguageChartColors = colours;

    this.sharedLanguageChartOptions["title"]["text"] = this.currentNewspaper + this.GrammarChecker(this.currentNewspaper) + " distribution of articles sharing language with party manifestos";
  }

   /**
   * Each manifesto has a set of top words, using a count vectoriser
   * And displayed in word cloud
   */  
  constructManifestoWordCloud() {
    let tempData: CloudData[] = [];

    for (let key in this.partyTopWords) {
      let text = key;
      let weight = this.partyTopWords[key] * 100;
      weight = +weight.toFixed()
      let tooltip = "Appeared " + weight.toString() + " times"; // TODO fix this?
      tempData.push({ text: text, weight: weight });
    }

    const changedData$: Observable<CloudData[]> = of(tempData);
    changedData$.subscribe(res => this.manifestoWordCloudData = res);

    //this.wordCloudComponent.reDraw();
  }

  /**
   * Each article has a set of top words, using a count vectoriser
   * Cumulated top words are retrieved
   * And displayed in word cloud
   */  
  constructArticlesWordCloud() {
    let tempData: CloudData[] = [];

    let sortedValues = [];
    for (let key in this.newspaperTopWords) {
      let value = this.newspaperTopWords[key];
      sortedValues.push(value);
    }

    sortedValues = sortedValues.sort();
    sortedValues = sortedValues.slice(0, 50);

    let top50Words = {}
    for (let key in this.newspaperTopWords) {
      if (Object.keys(top50Words).length == 50) {
        break;
      }

      let value = this.newspaperTopWords[key];
      if (value in sortedValues) {
        top50Words[key] = value;
      }
    }

    for (let key in top50Words) {
      let text = key;
      let weight = top50Words[key];
      let tooltip = "Appeared " + weight.toString() + " times";
      tempData.push({ text: text, weight: weight });
    }

    const changedData$: Observable<CloudData[]> = of(tempData);
    changedData$.subscribe(res => this.articlesWordCloudData = res);

    this.wordCloudComponent.reDraw();
  }

  /**
   * Sets meta-info string at bottom of screen, saying range of articles analysed, and how many analysed
   * @param startDate Earliest article analysed
   * @param endDate Latest article analysed
   */
  setMetaInfo(startDate, endDate) {
    if (this.startDate != "") {
      startDate = new Date(this.startDate).toLocaleString("en-GB").split(",")[0];
    } else {
      startDate = new Date(startDate).toLocaleString("en-GB").split(",")[0];
    }

    if (this.endDate != "") {
      endDate = new Date(this.endDate).toLocaleString("en-GB").split(",")[0];
    } else {
      endDate = new Date(endDate).toLocaleString("en-GB").split(",")[0];
    }

    this.metaInformation = String(this.analysedArticlesCount) + " articles analysed, from " + startDate + " to " + endDate
  }

  /**
   * Returns selected author - used for form control, and drawing of new charts for each author's data
   */
  get selectedAuthor() { return this.authorsForm.get('selectedAuthor'); }

  /**
   * Event called whenever author is changed in select box (in order to plot correct data for that author)
   * @param event Name of the author - used to access dictionary of authors -> author's opinions about topics/parties
   */
  public newAuthor(event: string) {
    this.plotAuthorTopicOpinionGraph(event);
    this.plotAuthorPartyOpinionGraph(event);
    this.authorSelected = true;
  }

  /**
   * Compares dates - used to sort a list of dates, for plotting
   * @param a First date
   * @param b Second date
   */
  public DateComparator(a, b) {
    let date1 = new Date(a[0]);
    let date2 = new Date(b[0])
    if (date1 < date2) return -1;
    if (date1 > date2) return 1;
    return 0;
  }

  /**
   * Checks if an article should be analysed
   * Using the user's set date ranges (if set - if not set, ignored)
   * @param current_date Date of current article being analysed
   */
  public DateRangeCheck(current_date) {
    let date = new Date(current_date);

    let absolute_min = new Date(2019, 7, 22);
    let start = null
    let end = null

    if (date >= absolute_min) {

      if (this.startDate != "") {
        start = new Date(this.startDate);
      }

      if (this.endDate != "") {
        end = new Date(this.endDate);
      }

      if (start == null || date >= start) {
        if (end == null || date <= end) {
          return true;
        }
      }
    }

    return false;
  }

  /**
   * Adds correct grammatical ending to a word - for aesthetics
   * @param word Word to have checked - i.e. "BBC News" needs an ', whereas 'Daily Mail' needs 's
   */
  public GrammarChecker(word: string) {
    if (word[word.length - 1] == "s") {
      return "'";
    } else {
      return "'s";
    }
  }

  /**
   * If a title is too long, can be split over multiple lines
   * This function handles this
   * @param str Title to be formatted
   */
  public formatTitle(str) : string[] {
    var sections = [];
    var words = str.split(" ");
    var temp = "";

    let maxWidth = 20;

    words.forEach(function (item, index) {
      if (temp.length > 0) {
        var concat = temp + ' ' + item;

        if (concat.length > maxWidth) {
          sections.push(temp);
          temp = "";
        }
        else {
          if (index == (words.length - 1)) {
            sections.push(concat);
            return;
          }
          else {
            temp = concat;
            return;
          }
        }
      }

      if (index == (words.length - 1)) {
        sections.push(item);
        return;
      }

      if (item.length < maxWidth) {
        temp = item;
      }
      else {
        sections.push(item);
      }

    });

    console.log(sections)
    return sections;
  }

}
