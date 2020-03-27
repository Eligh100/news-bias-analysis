import { Component, OnInit, ViewChild } from '@angular/core';
import { AnalysisParametersService } from '../analysis-parameters.service';
import { CloudData, CloudOptions, TagCloudComponent } from 'angular-tag-cloud-module';
import { Observable, of } from 'rxjs';

@Component({
  selector: 'app-bias-analysis-screen',
  templateUrl: './bias-analysis-screen.component.html',
  styleUrls: ['./bias-analysis-screen.component.css']
})
export class BiasAnalysisScreenComponent implements OnInit {

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
    "Conservatives": ["#0095FF","#42B1FF"],
    "Liberal Democrats": ["#FF5900", "#F7752F"],
    "Brexit Party": ["#0004ff", "#6669fa"],
    "Green": ["#04ff00", "#77ff75"],
    "SNP": ["#ffe600", "#fced60"],
    "Plaid Cymru": ["#00630c", "#2c6333"],
    "UKIP": ["#7300ff", "#ac6bfa"]
  };

  public canvasWidth = 500
  public needleValue = 100
  public centralLabel = ''
  public bottomLabel = ''
  public options = {
      hasNeedle: true,
      needleColor: 'gray',
      needleUpdateSpeed: 3000,
      arcColors: ['rgb(255, 17, 0)', 'rgb(169, 176, 167)', 'rgb(43,184,0)'],
      arcDelimiters: [40, 60],
      rangeLabel: ['Negative', 'Positive'],
      needleStartValue: 50,
  }

  public lineChart: string = "line";
  public doughnutChart: string = "doughnut";
  public radarChart: string = "radar";

  public biasChangeChartData: Array<any> = [{}];
  public biasChangeChartLabels: Array<any> = [];

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
      xAxes: [{ type: 'time', time: { unit: 'month', scaleLabel: {display: true, fontStyle: 'italic', labelString: "Article Publish Date"}  } }],
      yAxes: [ { id: 'y-axis-1', type: 'linear', position: 'left', ticks: { min: 0, max: 100 , } , scaleLabel: {display: true, fontStyle: 'italic', labelString: "Bias Score"} }, ]
    }
  };

  public topicOpinionChangeChartData: Array<any> = [
    { data: [], label: 'Scotland' },
    { data: [], label: 'Ireland' },
    { data: [], label: 'Wales' },
    { data: [], label: 'Brexit/EU' },
    { data: [], label: 'Economy/Business' },
    { data: [], label: 'Healthcare/NHS' },
    { data: [], label: 'Foreign Affairs' },
    { data: [], label: 'Racism' },
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
      xAxes: [{ type: 'time', time: { unit: 'month' }, scaleLabel: {display: true, fontStyle: 'italic', labelString: "Article Publish Date"} }],
      yAxes: [ { id: 'y-axis-1', type: 'linear', position: 'left', ticks: { min: -1, max: 1, callback: function(value) {
        if (value == 1) { 
          return value + " (Positive opinion)"; 
        } else if (value == 0) {
          return value + " (Neutral opinion)"; 
        } else if (value == -1) {
          return value + " (Negative opinion)"; 
        } else {
          return value.toFixed(1)
        }
      }}, scaleLabel: {display: true, fontStyle: 'italic', labelString: "Topic Polarity"}  }, ]
    }
  };

  public partyOpinionChangeChartData: Array<any> = [
    { data: [], label: 'Labour' },
    { data: [], label: 'Conservatives' },
    { data: [], label: 'Liberal Democrats' },
    { data: [], label: 'Brexit Party' },
    { data: [], label: 'Green' },
    { data: [], label: 'SNP' },
    { data: [], label: 'Plaid Cymru' },
    { data: [], label: 'UKIP' }
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
      xAxes: [{ type: 'time', time: { unit: 'month' }, scaleLabel: {display: true, fontStyle: 'italic', labelString: "Article Publish Date"} }],
      yAxes: [ { id: 'y-axis-1', type: 'linear', position: 'left', ticks: { min: -1, max: 1, callback: function(value) {
        if (value == 1) { 
          return value + " (Positive opinion)"; 
        } else if (value == 0) {
          return value + " (Neutral opinion)"; 
        } else if (value == -1) {
          return value + " (Negative opinion)"; 
        } else {
          return value.toFixed(1)
        }
      }}, scaleLabel: {display: true, fontStyle: 'italic', labelString: "Topic Polarity"}  }, ]
    }
  };

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

  public topicPopularityChartData: Array<any> = [];
  public topicPopularityChartLabels: Array<any> = [];
  public topicPopularityChartColors: Array<any> = [];

  public topicPopularityChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Topics polarity in [NEWSPAPER_NAME]",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    maintainAspectRatio: true,
    scale: {
      ticks: { min: 0, max: 100 , }
    }
  };

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

  public partyPopularityChartData: Array<any> = [];
  public partyPopularityChartLabels: Array<any> = [];
  public partyPopularityChartColors: Array<any> = [];

  public partyPopularityChartOptions: any = {
    responsive: true,
    title: {
      display: true,
      text: "Parties polarity in [NEWSPAPER_NAME]",
      fontSize: 30,
      fontFamily: "Roboto, 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif"
    },
    maintainAspectRatio: true,
    scale: {
      ticks: { min: 0, max: 100 , }
    }
  };

  @ViewChild(TagCloudComponent, {static: false}) wordCloudComponent: TagCloudComponent;

  public cloudOptions: CloudOptions = {
    // if width is between 0 and 1 it will be set to the size of the upper element multiplied by the value 
    width: 1,
    height: 300,
    overflow: false,
  };

  public manifestoWordCloudData: CloudData[] = []; // Word cloud data object of manifestos
  public articlesWordCloudData: CloudData[] = []; // Word cloud data object of articles

  public parties_information; // JSON object with 'parties-table' entries
  public articles_information; // JSON object with 'articles-table' entries
  public temp_info;

  public partyTopicScores = {};
  public partyToOtherPartiesScores = {};
  public partyTopWords = {};

  public newspaperTopWords = {}

  public mostDiscussedArticleTopics = {
    "Scotland": 0,
    "Ireland": 0,
    "Wales": 0,
    "Brexit/EU": 0,
    "Economy/Business": 0,
    "Healthcare/NHS": 0,
    "Foreign Affairs": 0,
    "Racism": 0,
    "Environment/Climate Change": 0,
    "Law/Police": 0,
    "Education/Schools": 0,
    "Immigration": 0
  }

  public mostDiscussedArticleParties = {
    "Labour": 0,
    "Conservatives": 0,
    "Liberal Democrats": 0,
    "Brexit Party": 0,
    "Green": 0,
    "SNP": 0,
    "Plaid Cymru": 0,
    "UKIP": 0
  }

  public overallTopicOpinions = {
    "Scotland": 0,
    "Ireland": 0,
    "Wales": 0,
    "Brexit/EU": 0,
    "Economy/Business": 0,
    "Healthcare/NHS": 0,
    "Foreign Affairs": 0,
    "Racism": 0,
    "Environment/Climate Change": 0,
    "Law/Police": 0,
    "Education/Schools": 0,
    "Immigration": 0
  }

  public overallPartyOpinions = {
    "Labour": 0,
    "Conservatives": 0,
    "Liberal Democrats": 0,
    "Brexit Party": 0,
    "Green": 0,
    "SNP": 0,
    "Plaid Cymru": 0,
    "UKIP": 0
  }

  public similarToPartyText = {
    "Labour": 0,
    "Conservatives": 0,
    "Liberal Democrats": 0,
    "Brexit Party": 0,
    "Green": 0,
    "SNP": 0,
    "Plaid Cymru": 0,
    "UKIP": 0
  }

  public currentParty;

  public newspaperToPartyBiasScore = 50;

  public dateToPartyBiasScore = {}; // filled with key: date and values: bias scores - to be plotted
  public dateToTopicScores = {}; // key: date, value: {} of key: topic, value: score
  public dateToPartyScores = {}; // key: date, value: {} of key: party, value: score

  public metaInformation: string = "";

  public startDate;
  public endDate;

  public analysedArticlesCount = 0;

  constructor(private _analysisParametersService: AnalysisParametersService) { }

  ngOnInit() {
    //this.needleValue = Math.floor(Math.random() * Math.floor(100));
    this.needleValue = 50;

    this.articles_information = "";

    this.getMetadata();
    this.getPartiesInformation();
    this.getArticlesInformation();
  }

  getMetadata(){
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

  getPartiesInformation() {
    this._analysisParametersService.getPartyInformation().subscribe(
      // the first argument is a function which runs on success
      data => { this.parties_information = data["partiesInfo"][0]},
      // the second argument is a function which runs on error
      err => console.error(err),
      // the third argument is a function which runs on completion
      () => {
        console.log('done loading parties info');
        this.encodePartyInfo()
      }
    );
  }

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
        console.log('done loading articles');

        let lastEvaluatedKey = ""

        if (this.articles_information['articleInfo']) {
          try {
            this.temp_info = JSON.parse(this.temp_info)
          } catch {
            let sliceIndex = this.temp_info.indexOf("\"lastEvaluatedKey\"");

            this.temp_info = this.temp_info.slice(0, (sliceIndex-13)) + " " + this.temp_info.slice(sliceIndex-12)
            this.temp_info = JSON.parse(this.temp_info)
          }
          this.articles_information["articleInfo"] = this.articles_information["articleInfo"].concat(this.temp_info["articleInfo"])
          lastEvaluatedKey = this.temp_info["lastEvaluatedKey"]
        } else {
          
          try {
            this.articles_information = JSON.parse(this.articles_information)
          } catch {
            let sliceIndex = this.articles_information.indexOf("\"lastEvaluatedKey\"");

            this.articles_information = this.articles_information.slice(0, (sliceIndex-13)) + " " + this.articles_information.slice(sliceIndex-12)
            this.articles_information = JSON.parse(this.articles_information)
          }

          lastEvaluatedKey = this.articles_information["lastEvaluatedKey"]
        
        }

        if (lastEvaluatedKey != "") {
          this._analysisParametersService.lastEvaluatedKey = lastEvaluatedKey;
          this.getArticlesInformation();
        } else {
          this.articles_information = this.articles_information["articleInfo"];
          this.analyseArticleInformation()
        }
      }
    );
  }

  encodePartyInfo(){
    let topic_sentiment_matrix_string = this.parties_information["topicsSentimentMatrix"];

    topic_sentiment_matrix_string.split(", ").forEach( (topicAndScore) => {
      let split = topicAndScore.split(" = ");
      let topicScore = +(split[1]);
      topicScore = +topicScore.toFixed(2);
      this.partyTopicScores[split[0]] = topicScore;
    });

    let party_sentiment_matrix_string = this.parties_information["partiesSentimentMatrix"];

    party_sentiment_matrix_string.split(", ").forEach( (partyAndScore) => {
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

  analyseArticleInformation(){
    this.articles_information.forEach( (article) => {

      let articlePubDate = article["articlePubDate"];

      if (articlePubDate != "NO INFO" && articlePubDate != ""){
        if (!this.DateRangeCheck(articlePubDate)){
          return;
        }
      } else{
        if (this.startDate != "" && this.endDate != ""){
          return;
        }
      }
      
      this.analysedArticlesCount++;

      let articlePartyBiasScore = 0 // current article's party bias score

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

      // Get headline and article topic sentiments
      // If they align (i.e. positive/negative) with party's view, add to overall bias score
      // Round to 2 d.p
      // If they don't align, subtract from overall bias score
      // Add/subtract score - take 1, and subtract difference (i.e. if party=0.8, and article=0.4, 1 - 0.4 = 0.6 to score)
      let headline_topic_sentiments = article["headlineTopicSentiments"]
      if (headline_topic_sentiments != "NO INFO"){
        headline_topic_sentiments.split(", ").forEach(element => {
          let split = element.split(" = ");
          let headline_score = +(split[1])
          headline_score = +headline_score.toFixed(2)
          if (this.partyTopicScores[split[0]]){
            if (this.partyTopicScores[split[0]] < 0 && headline_score < 0 || this.partyTopicScores[split[0]] > 0 && headline_score > 0){ // if same polarity
              let difference = Math.abs(this.partyTopicScores[split[0]] - headline_score)
              articlePartyBiasScore += 1 - difference
            } else if (this.partyTopicScores[split[0]] > 0 && headline_score < 0 || this.partyTopicScores[split[0]] < 0 && headline_score > 0){ // if different 
              let difference = Math.abs(this.partyTopicScores[split[0]] - headline_score)
              articlePartyBiasScore -= difference 
            } else { // if both zero (i.e. neutral)
              articlePartyBiasScore += 1;
            }
          }
          this.overallTopicOpinions[split[0]] += headline_score;
        });
      }

      // TODO if article negative about topic, but headline positive - switch polarity (and vice versa)
      let headline_party_sentiments = article["headlinePartySentiments"];
      if (headline_party_sentiments != "NO INFO"){
        headline_party_sentiments.split(", ").forEach(element => {
          let split = element.split(" = ");
          let headline_score = +(split[1])
          headline_score = +headline_score.toFixed(2)
          if (this.partyToOtherPartiesScores[split[0]]){
            if (this.partyToOtherPartiesScores[split[0]] < 0 && headline_score < 0 || this.partyToOtherPartiesScores[split[0]] > 0 && headline_score > 0){ // if same polarity
              let difference = Math.abs(this.partyToOtherPartiesScores[split[0]] - headline_score)
              articlePartyBiasScore += 20 - (difference * 20)
            } else if (this.partyToOtherPartiesScores[split[0]] > 0 && headline_score < 0 || this.partyToOtherPartiesScores[split[0]] < 0 && headline_score > 0){ // if different 
              let difference = Math.abs(this.partyToOtherPartiesScores[split[0]] - headline_score)
              articlePartyBiasScore -= (difference / 2) * 20
            } else { // if both zero (i.e. neutral)
              articlePartyBiasScore += 20;
            }
          } else if (split[0] == this.currentParty) { // If the headline has an opinion about the party in question
            articlePartyBiasScore += headline_score * 20
          }
          this.overallPartyOpinions[split[0]] += headline_score;
        });
      }

      let topics_to_sentiment = {};

      let article_topic_sentiments = article["articleTopicSentiments"]
      if (article_topic_sentiments != "NO INFO") {
        article_topic_sentiments.split(", ").forEach(element => {
          let split = element.split(" = ");
          let article_score = +(split[1])
          article_score = +article_score.toFixed(2)
          if (this.partyTopicScores[split[0]]){
            if (this.partyTopicScores[split[0]] < 0 && article_score < 0 || this.partyTopicScores[split[0]] > 0 && article_score > 0){ // if same polarity
              let difference = Math.abs(this.partyTopicScores[split[0]] - article_score)
              articlePartyBiasScore += 20 - (difference * 20)
            } else if (this.partyTopicScores[split[0]] > 0 && article_score <= 0 || this.partyTopicScores[split[0]] <= 0 && article_score > 0){ // if different 
              let difference = Math.abs(this.partyTopicScores[split[0]] - article_score)
              articlePartyBiasScore -= (difference / 2) * 20
            } else { // if both zero (i.e. neutral)
              articlePartyBiasScore += 20;
            }
          }
          this.overallTopicOpinions[split[0]] += article_score;
          topics_to_sentiment[split[0]] = article_score;
        });
      }

      let parties_to_sentiment = {};

      let article_party_sentiments = article["articlePartySentiments"]
      if (article_party_sentiments != "NO INFO") {
        article_party_sentiments.split(", ").forEach(element => {
          let split = element.split(" = ");
          let article_score = +(split[1])
          article_score = +article_score.toFixed(2)
          if (this.partyToOtherPartiesScores[split[0]]){
            if (this.partyToOtherPartiesScores[split[0]] < 0 && article_score < 0 || this.partyToOtherPartiesScores[split[0]] > 0 && article_score > 0){ // if same polarity
              let difference = Math.abs(this.partyToOtherPartiesScores[split[0]] - article_score)
              articlePartyBiasScore += 10 - (difference * 20)
            } else if (this.partyToOtherPartiesScores[split[0]] > 0 && article_score <= 0 || this.partyToOtherPartiesScores[split[0]] <= 0 && article_score > 0){ // if different 
              let difference = Math.abs(this.partyToOtherPartiesScores[split[0]] - article_score)
              articlePartyBiasScore -= (difference / 2) * 20
            } else { // if both zero (i.e. neutral)
              articlePartyBiasScore += 20;
            }
          } else if (split[0] == this.currentParty){ // If the article has an opinion about the party in question
            articlePartyBiasScore += article_score * 20;
          }
          this.overallPartyOpinions[split[0]] += article_score;
          parties_to_sentiment[split[0]] = article_score;
        });
      }

      // Get most likely party, and store
      let mostLikelyParty = article["mostLikelyParty"]
      this.similarToPartyText[article[mostLikelyParty]] += 1;

      // If the article is most similar to the current parties manifesto, add 10 to bias score
      if (mostLikelyParty == this.currentParty){
        articlePartyBiasScore += 10;
      } else {
        // If article is using language similar to the Labour manifesto
        // And we are evaluating the Conservative Party
        // Since the Conservative Party has a negative opinion on the Labour party, we can say
        // That the article is biased AGAINST the Conservative party
        // Add or subtract 10, weighted by the current party's opinion about the article's most similar party
        if (this.partyToOtherPartiesScores[mostLikelyParty]) {
          articlePartyBiasScore += this.partyToOtherPartiesScores[mostLikelyParty] * 10
        }
      }

      // Get the top words, and store in dict - if exists, update with frequency
      if (article["topWords"] != "NO INFO"){
        article["topWords"].split(", ").forEach(element => {
          let split = element.split(" = ");
          let word = split[0]
          let word_freq = +(split[1])
          word_freq = +word_freq.toFixed(2)
          if (this.newspaperTopWords[word]) { // if exists, add to score
            this.newspaperTopWords[split[0]] += word_freq;
          } else { // otherwise, make new entry
            this.newspaperTopWords[split[0]] = word_freq;
          }
        });
      }
   
      //console.log(articlePartyBiasScore)
      articlePartyBiasScore = +articlePartyBiasScore.toFixed(1);
      //let cumulative = articlePartyBiasScore / 100;
      articlePartyBiasScore = 50 + articlePartyBiasScore

      if (articlePartyBiasScore < 0) {
        articlePartyBiasScore = 0;
      } else if (articlePartyBiasScore > 100) {
        articlePartyBiasScore = 100;
      }
 
      this.newspaperToPartyBiasScore += articlePartyBiasScore;//cumulative

      //console.log(cumulative)
      // console.log(this.newspaperToPartyBiasScore)
      // console.log("---\n")

      if (articlePubDate != "NO INFO" && articlePubDate != ""){
        if (!this.dateToPartyBiasScore[articlePubDate]){
          this.dateToPartyBiasScore[articlePubDate] = []
        } 
        this.dateToPartyBiasScore[articlePubDate].push(articlePartyBiasScore)

        if (!this.dateToTopicScores[articlePubDate]){
          this.dateToTopicScores[articlePubDate] = {}
        }

        for (let key in topics_to_sentiment) {
          if (!this.dateToTopicScores[articlePubDate][key]) {
            this.dateToTopicScores[articlePubDate][key] = [];
          }
          this.dateToTopicScores[articlePubDate][key].push(topics_to_sentiment[key])
        }

        if (!this.dateToPartyScores[articlePubDate]){
          this.dateToPartyScores[articlePubDate] = {}
        }

        for (let key in parties_to_sentiment) {
          if (!this.dateToPartyScores[articlePubDate][key]) {
            this.dateToPartyScores[articlePubDate][key] = [];
          }
          this.dateToPartyScores[articlePubDate][key].push(parties_to_sentiment[key])
        }
      }
    })

    let finalBiasValue = this.newspaperToPartyBiasScore / this.analysedArticlesCount
    
    if (finalBiasValue < 0) {
      finalBiasValue = 0;
    } else if (finalBiasValue > 100) {
      finalBiasValue = 100;
    }

    this.needleValue = finalBiasValue
    console.log(this.needleValue)

    this.plotBiasChangeGraph();

    this.plotTopicChangeGraph();
    this.plotPartyChangeGraph();

    this.constructDiscussedTopicsDoughnut();
    this.constructTopicsPopularityDoughnut();

    this.constructDiscussedPartiesDoughnut();
    this.constructPartiesPopularityDoughnut();

    this.constructManifestoWordCloud();
    this.constructArticlesWordCloud();
  }

  plotBiasChangeGraph() {
    let data = [];
    let label = "Party bias change over time";

    let tempChartData = []
    let tempChartLabels = []

    let sortedDatesAndScore = [];

    for (let key in this.dateToPartyBiasScore){

      let scores = this.dateToPartyBiasScore[key];

      let total = 0;

      for (let i = 0; i < scores.length; i++){
        total += scores[i];
      }

      let average = total / scores.length

      sortedDatesAndScore.push([key, average])
    }

    sortedDatesAndScore = sortedDatesAndScore.sort(this.DateComparator);

    this.setMetaInfo(sortedDatesAndScore[0][0], sortedDatesAndScore[sortedDatesAndScore.length - 1][0]);

    for (let i = 0; i < sortedDatesAndScore.length; i++) {
      tempChartLabels.push(sortedDatesAndScore[i][0]);
      data.push(sortedDatesAndScore[i][1]);
    }
    
    tempChartData.push({data: data, label: label, fill: false, pointRadius : 2, pointBorderColor: "black"});

    this.biasChangeChartData = tempChartData;
    this.biasChangeChartLabels = tempChartLabels;

  }

  plotTopicChangeGraph() {
    let data = [];
    let label = "[Newspaper] topic opinions change over time";

    let tempChartData = this.topicOpinionChangeChartData;
    let tempChartLabels = []
    let tempColours = []

    let sortedDatesAndTopicScoreDict = [];

    for (let date in this.dateToTopicScores){

      let topicScoreDict = this.dateToTopicScores[date];

      sortedDatesAndTopicScoreDict.push([date, topicScoreDict]);
    }

    sortedDatesAndTopicScoreDict = sortedDatesAndTopicScoreDict.sort(this.DateComparator);

    for (let i = 0; i < sortedDatesAndTopicScoreDict.length; i++) {
      let date = sortedDatesAndTopicScoreDict[i][0];
      let topicScoreDict = sortedDatesAndTopicScoreDict[i][1];

      tempChartLabels.push(date);
      
      let counter = 0
      for (let topic in this.topicColours) {
        if (topicScoreDict[topic]){ // if any articles from this date DO mention x topic

          let scores = topicScoreDict[topic];
          let total = 0;
          for (let i = 0; i < scores.length; i++){
            let score = scores[i]
            if (score < -1) {
              score = -1
            } else if (score > 1) {
              score = 1
            }
            total += score;
          }
          let average = total / scores.length

          tempChartData[counter]["data"].push(average)
        } else { // if any articles from this date DON'T mention x topic
          tempChartData[counter]["data"].push(null)
        }

        tempChartData[counter]["fill"] = false;
        tempChartData[counter]["pointRadius"] = 2;
        tempChartData[counter]["pointBorderColor"] = "black";

        if (counter != 0) {
          tempChartData[counter]["hidden"] = true;
        }

        tempColours.push({backgroundColor: this.topicColours[topic][0], borderColor: this.topicColours[topic][1]});

        counter++;
      }
    }

    this.topicOpinionChangeChartData = tempChartData;
    this.topicOpinionChangeChartLabels = tempChartLabels;
    this.topicOpinionChangeChartColors = tempColours;

  }

  plotPartyChangeGraph() {
    let data = [];
    let label = "[Newspaper] party opinions change over time";

    let tempChartData = this.partyOpinionChangeChartData;
    let tempChartLabels = []
    let tempColours = []

    let sortedDatesAndPartyScoreDict = [];

    for (let date in this.dateToPartyScores){

      let dateScoreDict = this.dateToPartyScores[date];

      sortedDatesAndPartyScoreDict.push([date, dateScoreDict]);
    }

    sortedDatesAndPartyScoreDict = sortedDatesAndPartyScoreDict.sort(this.DateComparator);

    for (let i = 0; i < sortedDatesAndPartyScoreDict.length; i++) {
      let date = sortedDatesAndPartyScoreDict[i][0];
      let partyScoreDict = sortedDatesAndPartyScoreDict[i][1];

      tempChartLabels.push(date);
      
      let counter = 0
      for (let party in this.partyColours) {
        if (partyScoreDict[party]){ // if any articles from this date DO mention x topic

          let scores = partyScoreDict[party];
          let total = 0;
          for (let i = 0; i < scores.length; i++){
            let score = scores[i]
            if (score < -1) {
              score = -1
            } else if (score > 1) {
              score = 1
            }
            total += score;
          }
          let average = total / scores.length

          tempChartData[counter]["data"].push(average)
        } else { // if any articles from this date DON'T mention x topic
          tempChartData[counter]["data"].push(null)
        }

        tempChartData[counter]["fill"] = false;
        tempChartData[counter]["pointRadius"] = 2;
        tempChartData[counter]["pointBorderColor"] = "black";

        if (counter != 0) {
          tempChartData[counter]["hidden"] = true;
        }

        tempColours.push({backgroundColor: this.partyColours[party][0], borderColor: this.partyColours[party][1]});

        counter++;
      }
    }

    this.partyOpinionChangeChartData = tempChartData;
    this.partyOpinionChangeChartLabels = tempChartLabels;
    this.partyOpinionChangeChartColors = tempColours;

  }

  constructDiscussedTopicsDoughnut() {
    let tempDoughnutData = [];
    let doughnutData = [];

    let doughnutLabels = [];

    let tempColours = [];
    let doughnutMainColours = [];
    let doughnutHoverColours = [];

    for (let key in this.mostDiscussedArticleTopics) {
      if (key != "NO INFO" && key != "undefined"){
        doughnutLabels.push(key);

        let value = this.mostDiscussedArticleTopics[key];
        doughnutData.push(value);

        try{
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

    tempDoughnutData.push({data: doughnutData, label: "Topic discussion frequency over all articles"})

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

  }

  constructTopicsPopularityDoughnut() {
    let data = [];
    let label = "Newspaper's opinions on topics";
    let colours = [];

    let tempData = [];
    let radarLabels = [];

    for (let key in this.overallTopicOpinions) {
      if (key != "NO INFO" && key != "" && key != undefined){
        let value = this.overallTopicOpinions[key];
        if (value > 1) {
          value = 1
        } else if (value < -1){
          value = -1
        }

        if (value < 0) {
          value = Math.abs(value)
          value = value / 2
          value = 0 + (value * 100)
        } else if (value > 0) {
          value = Math.abs(value)
          value = value / 2
          value = 50 + (value * 100)
        } else {
          value = 50;
        }

        data.push(value)
        radarLabels.push(key)
        colours.push(this.topicColours[key][0])
      }
    }

    tempData.push({data: data, label: label, pointBackgroundColor: colours, borderColor: "#878787", radius: 6, pointRadius: 6, pointBorderColor: "black" });
    
    this.topicPopularityChartData = tempData;
    this.topicPopularityChartLabels = radarLabels;
    this.topicPopularityChartColors = colours;
  }

  constructDiscussedPartiesDoughnut() {
    let tempDoughnutData = [];
    let doughnutData = [];

    let doughnutLabels = [];

    let tempColours = [];
    let doughnutMainColours = [];
    let doughnutHoverColours = [];

    for (let key in this.mostDiscussedArticleParties) {
      if (key != "NO INFO" && key != "undefined"){
        doughnutLabels.push(key);

        let value = this.mostDiscussedArticleParties[key];
        doughnutData.push(value);

        try{
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

    tempDoughnutData.push({data: doughnutData, label: "Party discussion frequency over all articles"})

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

  }

  constructPartiesPopularityDoughnut() {
    let data = [];
    let label = "Newspaper's opinions on parties";
    let colours = [];

    let tempData = [];
    let radarLabels = [];

    for (let key in this.overallPartyOpinions) {
      if (key != "NO INFO" && key != "" && key != undefined){
        let value = this.overallPartyOpinions[key];
        if (value > 1) {
          value = 1
        } else if (value < -1){
          value = -1
        }

        if (value < 0) {
          value = Math.abs(value)
          value = value / 2
          value = 0 + (value * 100)
        } else if (value > 0) {
          value = Math.abs(value)
          value = value / 2
          value = 50 + (value * 100)
        } else {
          value = 50;
        }

        data.push(value)
        radarLabels.push(key)
        colours.push(this.partyColours[key][0])
      }
    }

    tempData.push({data: data, label: label, pointBackgroundColor: colours, borderColor: "#878787", radius: 6, pointRadius: 6, pointBorderColor: "black" });
    
    this.partyPopularityChartData = tempData;
    this.partyPopularityChartLabels = radarLabels;
    this.partyPopularityChartColors = colours;
  }


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

    this.wordCloudComponent.reDraw();
  }

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
      if (Object.keys(top50Words).length == 50){
        break;
      }

      let value = this.newspaperTopWords[key];
      if (value in sortedValues){
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

  setMetaInfo(startDate, endDate){
    if (this.startDate != ""){
      startDate = new Date(this.startDate).toLocaleString("en-GB").split(",")[0];
    } else {
      startDate = new Date(startDate).toLocaleString("en-GB").split(",")[0]; 
    }

    if (this.endDate != ""){
      endDate = new Date(this.endDate).toLocaleString("en-GB").split(",")[0];
    } else {
      endDate = new Date(endDate).toLocaleString("en-GB").split(",")[0]; 
    }

    this.metaInformation = String(this.analysedArticlesCount) + " articles analysed, from " + startDate + " to " + endDate
  }

  public DateComparator(a, b) {
    let date1 = new Date(a[0]);
    let date2 = new Date(b[0])
    if (date1 < date2) return -1;
    if (date1 > date2) return 1;
    return 0;
  }

  public DateRangeCheck(current_date) {
    let date = new Date(current_date);

    let absolute_min = new Date(2019, 7, 22);
    let start = null
    let end = null

    if (date >= absolute_min){

      if (this.startDate != ""){
        start = new Date(this.startDate);
      } 

      if (this.endDate != ""){
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

}
