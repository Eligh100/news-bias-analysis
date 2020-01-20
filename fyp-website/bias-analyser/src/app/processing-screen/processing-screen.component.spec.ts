import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ProcessingScreenComponent } from './processing-screen.component';

describe('ProcessingScreenComponent', () => {
  let component: ProcessingScreenComponent;
  let fixture: ComponentFixture<ProcessingScreenComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ProcessingScreenComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ProcessingScreenComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
