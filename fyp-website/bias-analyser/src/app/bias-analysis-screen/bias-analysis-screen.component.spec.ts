import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BiasAnalysisScreenComponent } from './bias-analysis-screen.component';

describe('BiasAnalysisScreenComponent', () => {
  let component: BiasAnalysisScreenComponent;
  let fixture: ComponentFixture<BiasAnalysisScreenComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BiasAnalysisScreenComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BiasAnalysisScreenComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
