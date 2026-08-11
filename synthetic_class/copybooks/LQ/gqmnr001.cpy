******************************************************************
*  COPYBOOK  : GQMNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : MN
******************************************************************
 01  RT-QMN-RATING.

          03 RT-QMN-TERRITORY-CODE            PIC X(3).
          03 RT-QMN-CLASS-CODE                PIC X(4).
          03 RT-QMN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QMN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QMN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QMN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QMN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QMN-RATED-PREMIUM             PIC 9(9)V9(2).
