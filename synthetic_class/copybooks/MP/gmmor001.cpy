******************************************************************
*  COPYBOOK  : GMMOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Medical Payments (MP)
*  STATE     : MO
******************************************************************
 01  RT-MMO-RATING.

          03 RT-MMO-TERRITORY-CODE            PIC X(3).
          03 RT-MMO-CLASS-CODE                PIC X(4).
          03 RT-MMO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-MMO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-MMO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-MMO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-MMO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-MMO-RATED-PREMIUM             PIC 9(9)V9(2).
