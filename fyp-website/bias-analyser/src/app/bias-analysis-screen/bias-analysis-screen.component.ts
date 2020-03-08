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

  public canvasWidth = 400
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

  @ViewChild(TagCloudComponent, {static: false}) wordCloudComponent: TagCloudComponent;

  public cloudOptions: CloudOptions = {
    // if width is between 0 and 1 it will be set to the size of the upper element multiplied by the value 
    width: 1,
    height: 300,
    overflow: true,
  };

  public manifestoWordCloudData: CloudData[] = [];
  public articlesWordCloudData: CloudData[] = [];

  public most_discussed_string = "";
  public overall_opinion_string = "";

  public parties_information;
  public articles_information;

  public partyTopicScores = {};
  public partyTopWords = {};

  public newspaperTopWords = {}

  public mostDiscussedArticleTopics = {
    "Labour": 0,
    "Conservatives/Government": 0,
    "Liberal Democrats": 0,
    "Scotland": 0,
    "Ireland": 0,
    "Brexit/EU": 0,
    "Economy/Business": 0,
    "Healthcare/NHS": 0,
    "Foreign Affairs": 0,
    "Racism": 0,
    "Environment/Climate Change": 0,
    "Law/Police": 0,
    "Education/Schools": 0,
    "Immigration": 0,
    "Wales": 0
  }

  public overallTopicOpinions = {
    "Labour": 0,
    "Conservatives/Government": 0,
    "Liberal Democrats": 0,
    "Scotland": 0,
    "Ireland": 0,
    "Brexit/EU": 0,
    "Economy/Business": 0,
    "Healthcare/NHS": 0,
    "Foreign Affairs": 0,
    "Racism": 0,
    "Environment/Climate Change": 0,
    "Law/Police": 0,
    "Education/Schools": 0,
    "Immigration": 0,
    "Wales": 0
  }

  public currentParty;

  public newspaperToPartyBiasScore = 0;

  constructor(private _analysisParametersService: AnalysisParametersService) { }

  ngOnInit() {
    //this.needleValue = Math.floor(Math.random() * Math.floor(100));
    this.needleValue = 69;

    this.getPartiesInformation();
    this.getArticlesInformation();
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
      data => { this.articles_information = data},//data["articleInfo"]},
      // the second argument is a function which runs on error
      err => console.error(err),
      // the third argument is a function which runs on completion
      () => {
        console.log('done loading articles');
        try {
          this.articles_information = JSON.parse(this.articles_information)
        } catch {
          this.articles_information = this.articles_information.slice(0, this.articles_information.length - 10) + " " + this.articles_information.slice(this.articles_information.length - 9)
          this.articles_information = JSON.parse(this.articles_information)
        }

        this.articles_information = this.articles_information["articleInfo"];
        this.analyseArticleInformation()
      }
    );
  }

  encodePartyInfo(){
    let topic_sentiment_matrix_string = this.parties_information["topicsSentimentMatrix"]

    topic_sentiment_matrix_string.split(", ").forEach( (topicAndScore) => {
      let split = topicAndScore.split(" = ");
      let topicScore = +(split[1])
      topicScore = +topicScore.toFixed(2)
      this.partyTopicScores[split[0]] = topicScore
    });

    this.currentParty = this.parties_information["partyName"]

    this.parties_information["topWords"].split(", ").forEach(element => {
      let split = element.split(" = ");
      let word_freq = +(split[1])
      word_freq = +word_freq.toFixed(2)
      this.partyTopWords[split[0]] = word_freq
    });
    console.log(this.partyTopWords)
  }

  analyseArticleInformation(){
    this.articles_information.forEach( (article) => {
      // Get the most likely topics, to display what the newspaper discusses the most
      let article_topics = (article["articleTopics"]).split(", ")

      article_topics.forEach(element => {
        this.mostDiscussedArticleTopics[element] += 1
      });

      // Get headline and article topic sentiments
      // If they align (i.e. positive/negative) with party's view, add to overall bias score
      // Round to 2 d.p
      // If they don't align, subtract from overall bias score
      // Add/subtract score - take 1, and subtract difference (i.e. if party=0.8, and article=0.4, 1 - 0.4 = 0.6 to score)
      let headline_sentiments = article["headline-topic-sentiments"]
      if (headline_sentiments != "NO INFO"){
        headline_sentiments.split(", ").forEach(element => {
          let split = element.split(" = ");
          let headline_score = +(split[1])
          headline_score = +headline_score.toFixed(2)
          if (this.partyTopicScores[split[0]]){
            if (this.partyTopicScores[split[0]] < 0 && headline_score < 0 || this.partyTopicScores[split[0]] > 0 && headline_score > 0){ // if same polarity
              let difference = Math.abs(this.partyTopicScores[split[0]] - headline_score)
              this.newspaperToPartyBiasScore += 1 - difference
            } else if (this.partyTopicScores[split[0]] > 0 && headline_score < 0 || this.partyTopicScores[split[0]] < 0 && headline_score > 0){ // if different 
              let difference = Math.abs(this.partyTopicScores[split[0]] - headline_score)
              this.newspaperToPartyBiasScore -= difference * 10
            } else { // if both zero (i.e. neutral)
              this.newspaperToPartyBiasScore += 1;
            }
          }
          this.overallTopicOpinions[split[0]] += headline_score;
        });
      }

      let article_sentiment_overall = 0

      let article_sentiments = article["articleTopicSentiments"]
      if (article_sentiments != "NO INFO") {
        article_sentiments.split(", ").forEach(element => {
          let split = element.split(" = ");
          let article_score = +(split[1])
          article_score = +article_score.toFixed(2)
          if (this.partyTopicScores[split[0]]){
            if (this.partyTopicScores[split[0]] < 0 && article_score < 0 || this.partyTopicScores[split[0]] > 0 && article_score > 0){ // if same polarity
              let difference = Math.abs(this.partyTopicScores[split[0]] - article_score)
              this.newspaperToPartyBiasScore += 1 - difference
            } else if (this.partyTopicScores[split[0]] > 0 && article_score <= 0 || this.partyTopicScores[split[0]] <= 0 && article_score > 0){ // if different 
              let difference = Math.abs(this.partyTopicScores[split[0]] - article_score)
              this.newspaperToPartyBiasScore -= difference
            } else { // if both zero (i.e. neutral)
              this.newspaperToPartyBiasScore += 1;
            }
          }
          this.overallTopicOpinions[split[0]] += article_score;
          article_sentiment_overall += article_score;
        });
      }

      if (article_sentiment_overall > 1) {
        article_sentiment_overall = 1;
      } else if (article_sentiment_overall < -1) {
        article_sentiment_overall = -1;
      }

      // If topic of article is THE party in question, add +10 or -10 accordingly
      if (this.currentParty == "Conservatives") {
        if (this.overallTopicOpinions["Conservatives/Government"]) { // if the conservatives are a mentioned topic
          if (this.overallTopicOpinions["Conservatives/Government"] > 1) {
            this.newspaperToPartyBiasScore += 10
          } else if (this.overallTopicOpinions["Conservatives/Government"] < -1) {
            this.newspaperToPartyBiasScore += -10
          } else {
            this.newspaperToPartyBiasScore += this.overallTopicOpinions["Conservatives/Government"] * 10
          }
        }
      } else {
        if (this.overallTopicOpinions[this.currentParty]) {
          if (this.overallTopicOpinions[this.currentParty] > 1) {
            this.newspaperToPartyBiasScore += 10
          } else if (this.overallTopicOpinions[this.currentParty] < -1) {
            this.newspaperToPartyBiasScore += -10
          } else {
            this.newspaperToPartyBiasScore += this.overallTopicOpinions[this.currentParty] * 10
          }
        }
      }

      // If most likely party is THE party in question, add +10 or -10 accordingly
      if (article["mostLikelyParty"] == this.currentParty){
        this.newspaperToPartyBiasScore += (article_sentiment_overall*10)
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

    })

    this.newspaperToPartyBiasScore = this.newspaperToPartyBiasScore / 10
    this.newspaperToPartyBiasScore = +this.newspaperToPartyBiasScore.toFixed(1)

    this.needleValue = this.newspaperToPartyBiasScore/2 + 50

    this.getMostDiscussedTopics();
    this.getOverallTopicOpinions();

    this.constructManifestoWordCloud();
    this.constructArticlesWordCloud();
  }

  getMostDiscussedTopics(){
    for (let key in this.mostDiscussedArticleTopics) {
      if (key != "NO INFO" && key != "undefined"){
        let value = this.mostDiscussedArticleTopics[key];
        this.most_discussed_string += key + ": Mentioned " + value.toString() + " times -/- "
      }
    }
  }

  getOverallTopicOpinions(){
    for (let key in this.overallTopicOpinions) {
      if (key != "NO INFO"){
        let value = this.overallTopicOpinions[key];
        if (value > 1) {
          value = 1
        } else if (value < -1){
          value = -1
        }

        let newspaper_overall_opinion = ""

        if (value >= -1 && value < -0.3){
          newspaper_overall_opinion = "Negative"
        } else if (value <= 1 && value > 0.3){
          newspaper_overall_opinion = "Positive"
        } else {
          newspaper_overall_opinion = "Neutral"
        } 

        this.overall_opinion_string += key + ": " + newspaper_overall_opinion + " -/- "
      }
    }
  }

  constructManifestoWordCloud(){
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

  constructArticlesWordCloud(){
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

}
