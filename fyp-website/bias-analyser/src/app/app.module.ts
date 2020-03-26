import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppRoutingModule } from './app-routing.module';
import { StartScreenComponent } from './start-screen/start-screen.component';
import { ProcessingScreenComponent } from './processing-screen/processing-screen.component';
import { BiasAnalysisScreenComponent } from './bias-analysis-screen/bias-analysis-screen.component';

import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatMomentDateModule } from '@angular/material-moment-adapter';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDividerModule } from '@angular/material/divider';
import { GaugeChartModule } from 'angular-gauge-chart';
import { TagCloudModule } from 'angular-tag-cloud-module';
import { ChartsModule } from 'angular-bootstrap-md';

import { HttpClientModule }    from '@angular/common/http';
import { MAT_DATE_LOCALE } from '@angular/material/core';

@NgModule({
  declarations: [
    AppComponent,
    StartScreenComponent,
    ProcessingScreenComponent,
    BiasAnalysisScreenComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    MatSelectModule,
    MatButtonModule,
    MatInputModule,
    MatMomentDateModule,
    MatDatepickerModule,
    MatProgressSpinnerModule,
    MatExpansionModule,
    MatDividerModule,
    GaugeChartModule,
    TagCloudModule,
    ChartsModule
  ],
  providers: [{provide: MAT_DATE_LOCALE, useValue: 'en_GB'},],
  bootstrap: [AppComponent]
})
export class AppModule { }
