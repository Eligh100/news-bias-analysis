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

  constructor(private router: Router, private route: ActivatedRoute, private analysisParameters: AnalysisParametersService) { }

  ngOnInit() {
    this.router.navigate([`../bias-analysis`], { relativeTo: this.route });
  }

}
