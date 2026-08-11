******************************************************************
*  COPYBOOK  : GONER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : NE
******************************************************************
 01  RT-ONE-RATING.

          03 RT-ONE-TERRITORY-CODE            PIC X(3).
          03 RT-ONE-CLASS-CODE                PIC X(4).
          03 RT-ONE-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ONE-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ONE-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ONE-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ONE-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ONE-RATED-PREMIUM             PIC 9(9)V9(2).
