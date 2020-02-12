import { Component, OnInit, Input } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormGroup } from '@angular/forms';
import { AnalysisParametersService } from '../analysis-parameters.service';

@Component({
  selector: 'app-processing-screen',
  templateUrl: './processing-screen.component.html',
  styleUrls: ['./processing-screen.component.css']
})
export class ProcessingScreenComponent implements OnInit {

  counter = 3;

  constructor(private router: Router, private route: ActivatedRoute, private analysisParameters: AnalysisParametersService) { }

  ngOnInit() {
    let intervalId = setInterval(() => {
        this.counter = this.counter - 1;
        if(this.counter === 0) this.goToBiasAnalysisScreen()
    }, 1000)
  }

  goToBiasAnalysisScreen(){
    this.router.navigate([`../bias-analysis`], { relativeTo: this.route });
    this.process();
  }

  process(){
    console.log(this.analysisParameters.analysisParameters.get("selectedNewspaper").value);
  }

}
