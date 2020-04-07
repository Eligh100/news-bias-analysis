import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'bias-analyser'; // tiny rat chef

  startScreen;

  constructor(private router: Router) {}

  ngOnInit() {
    this.router.navigate([''])
  }

}
