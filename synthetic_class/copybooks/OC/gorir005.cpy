******************************************************************
*  COPYBOOK  : GORIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : RI
******************************************************************
 01  RT-ORI-RATING.

          03 RT-ORI-TERRITORY-CODE            PIC X(3).
          03 RT-ORI-CLASS-CODE                PIC X(4).
          03 RT-ORI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ORI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ORI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ORI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ORI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ORI-RATED-PREMIUM             PIC 9(9)V9(2).
