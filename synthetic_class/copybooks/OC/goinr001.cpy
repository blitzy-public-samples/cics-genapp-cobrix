******************************************************************
*  COPYBOOK  : GOINR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : IN
******************************************************************
 01  RT-OIN-RATING.

          03 RT-OIN-TERRITORY-CODE            PIC X(3).
          03 RT-OIN-CLASS-CODE                PIC X(4).
          03 RT-OIN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OIN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OIN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OIN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OIN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OIN-RATED-PREMIUM             PIC 9(9)V9(2).
