******************************************************************
*  COPYBOOK  : GONJR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : NJ
******************************************************************
 01  RT-ONJ-RATING.

          03 RT-ONJ-TERRITORY-CODE            PIC X(3).
          03 RT-ONJ-CLASS-CODE                PIC X(4).
          03 RT-ONJ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ONJ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ONJ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ONJ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ONJ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ONJ-RATED-PREMIUM             PIC 9(9)V9(2).
