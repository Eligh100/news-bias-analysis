import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-processing-screen',
  templateUrl: './processing-screen.component.html',
  styleUrls: ['./processing-screen.component.css']
})
export class ProcessingScreenComponent implements OnInit {

  counter = 3;

  constructor(private router: Router, private route: ActivatedRoute) { }

  ngOnInit() {
    let intervalId = setInterval(() => {
        this.counter = this.counter - 1;
        console.log(this.counter)
        if(this.counter === 0) this.goToBiasAnalysisScreen()
    }, 1000)
  }

  goToBiasAnalysisScreen(){
    this.router.navigate([`../bias-analysis`], { relativeTo: this.route });
  }


}
