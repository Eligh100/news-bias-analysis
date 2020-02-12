import { TestBed } from '@angular/core/testing';

import { AnalysisParametersService } from './analysis-parameters.service';

describe('AnalysisParametersService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: AnalysisParametersService = TestBed.get(AnalysisParametersService);
    expect(service).toBeTruthy();
  });
});
