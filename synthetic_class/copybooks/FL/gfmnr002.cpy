******************************************************************
*  COPYBOOK  : GFMNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : MN
******************************************************************
 01  RT-FMN-RATING.

          03 RT-FMN-TERRITORY-CODE            PIC X(3).
          03 RT-FMN-CLASS-CODE                PIC X(4).
          03 RT-FMN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FMN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FMN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FMN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FMN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FMN-RATED-PREMIUM             PIC 9(9)V9(2).
