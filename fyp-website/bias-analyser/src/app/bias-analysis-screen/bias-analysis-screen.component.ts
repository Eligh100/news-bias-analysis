import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-bias-analysis-screen',
  templateUrl: './bias-analysis-screen.component.html',
  styleUrls: ['./bias-analysis-screen.component.css']
})
export class BiasAnalysisScreenComponent implements OnInit {

  public canvasWidth = 400
  public needleValue = 100
  public centralLabel = ''
  public bottomLabel = this.needleValue.toString();
  public options = {
      hasNeedle: true,
      needleColor: 'gray',
      needleUpdateSpeed: 5000,
      arcColors: ['rgb(255, 17, 0)', 'rgb(169, 176, 167)', 'rgb(43,184,0)'],
      arcDelimiters: [40, 60],
      rangeLabel: ['Negative', 'Positive'],
      needleStartValue: 0,
  }

  constructor() { }

  ngOnInit() {
  }

}
