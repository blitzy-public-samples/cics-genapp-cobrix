******************************************************************
*  COPYBOOK  : GNMNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : MN
******************************************************************
 01  RT-NMN-RATING.

          03 RT-NMN-TERRITORY-CODE            PIC X(3).
          03 RT-NMN-CLASS-CODE                PIC X(4).
          03 RT-NMN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NMN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NMN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NMN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NMN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NMN-RATED-PREMIUM             PIC 9(9)V9(2).
