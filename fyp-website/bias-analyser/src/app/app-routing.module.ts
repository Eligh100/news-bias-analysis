import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { StartScreenComponent } from './start-screen/start-screen.component';
import { ProcessingScreenComponent } from './processing-screen/processing-screen.component';
import { BiasAnalysisScreenComponent } from './bias-analysis-screen/bias-analysis-screen.component';

const routes: Routes = [
  { path: 'processing', component: ProcessingScreenComponent },
  { path: 'bias-analysis', component: BiasAnalysisScreenComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }