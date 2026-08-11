******************************************************************
*  COPYBOOK  : GOFLR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : FL
******************************************************************
 01  RT-OFL-RATING.

          03 RT-OFL-TERRITORY-CODE            PIC X(3).
          03 RT-OFL-CLASS-CODE                PIC X(4).
          03 RT-OFL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OFL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OFL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OFL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OFL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OFL-RATED-PREMIUM             PIC 9(9)V9(2).
