import { Injectable } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Injectable({
  providedIn: 'root'
})
export class AnalysisParametersService {

  analysisParameters: FormGroup

  constructor() { }
}
