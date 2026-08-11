******************************************************************
*  COPYBOOK  : GOILR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : IL
******************************************************************
 01  RT-OIL-RATING.

          03 RT-OIL-TERRITORY-CODE            PIC X(3).
          03 RT-OIL-CLASS-CODE                PIC X(4).
          03 RT-OIL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OIL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OIL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OIL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OIL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OIL-RATED-PREMIUM             PIC 9(9)V9(2).
