******************************************************************
*  COPYBOOK  : GMMNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MN
******************************************************************
 01  RT-MMN-RATING.

          03 RT-MMN-TERRITORY-CODE            PIC X(3).
          03 RT-MMN-CLASS-CODE                PIC X(4).
          03 RT-MMN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MMN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MMN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MMN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MMN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MMN-RATED-PREMIUM             PIC 9(9)V9(2).
