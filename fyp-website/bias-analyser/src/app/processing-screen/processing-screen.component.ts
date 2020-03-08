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

  counter = 1;

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
    /// Call service
    /// Service calls AWS lambda script
    /// Script does processing
    /// Script returns JSON response, with my data
    /// Service has data
    /// Component uses service's data (after some event saying data is available (i.e. switch from loading to finished))
  }

}
