******************************************************************
*  COPYBOOK  : GOMAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : MA
******************************************************************
 01  RT-OMA-RATING.

          03 RT-OMA-TERRITORY-CODE            PIC X(3).
          03 RT-OMA-CLASS-CODE                PIC X(4).
          03 RT-OMA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OMA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OMA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OMA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OMA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OMA-RATED-PREMIUM             PIC 9(9)V9(2).
